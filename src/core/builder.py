import logging
from typing import Optional, Union, Final, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse

from shared.enum import Environment
from shared.interfaces import BaseModule, BaseManager

logger = logging.getLogger("console")

class FastApiBuilder:
    def __init__(
        self, 
        environment: Environment,
        modules: list[BaseModule],
        managers: list[BaseManager],
        api_prefix: Optional[str] = None,
        *,
        global_depends: Optional[list[Union[Callable, type]]] = None,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        ) -> None:

        self.environment: Final[Environment] = environment
        not_prod = environment != "production"
        self.api_prefix = api_prefix or "/api"
        self._modules: list[BaseModule] = modules
        self._managers: list[BaseManager] = managers
        if global_depends:
            depends = [Depends(depends) for depends in global_depends]
        else:
            depends = None
        logger.debug("Running application in the environment: %s", self.environment)

        @asynccontextmanager
        async def lifespan(app):
            await self._startup_managers()
            await self._startup_tasks()
            yield
            await self._shutdown_managers()
            await self._shutdown_tasks()
        
        self.app: Final[FastAPI] = FastAPI(
            debug= not_prod,
            title=title or "Unofficial SkyMp MasterApi",
            summary=summary or "REST API application for monitoring SkyMp servers and authorizing clients for these servers",
            description=description or "The API is built on a modular system where each module is responsible for its own set of endpoints",
            version=version or "0.0.1",
            openapi_url= "/openapi.json" if not_prod else None,
            openapi_tags=self._tags_metadata() if self._modules else None,
            docs_url="/docs" if not_prod else None,
            redoc_url="/redoc" if not_prod else None,
            lifespan=lifespan,
            default_response_class=ORJSONResponse,
            dependencies=depends,
        )
        self._setup_modules()

    def _setup_modules(self) -> None:
        logger.debug("Setup modules:")
        if self._modules:
            try:
                for module in self._modules:
                    module._setup(environment=self.environment, app=self.app)
                    if module.router:
                        self.app.include_router(router=module.router, prefix=self.api_prefix)
                    
                    logger.info("[✓] %s", module.__str__())
            except Exception as e:
                    logger.warning("[☓] %s - %s", module.__str__(), e)
                    raise 
        else:
            logger.warning("No modules that can be loaded")

    def _tags_metadata(self) -> list[dict[str, str]]:
        tags_metadata = []
        if self._modules:
            for module in self._modules:
                if module.tags:
                    tags_metadata.append(
                        {"name": module.tags, "description": module.description}
                    )
        return tags_metadata

    async def _startup_tasks(self) -> None:
        logger.debug("Startup tasks")
        if self._modules:
            for module in self._modules:
                try:
                    await module.startup()
                except Exception as e:
                    logger.error("Failed to start module %s: %s", module.name, e, exc_info=True)
                    raise

    async def _shutdown_tasks(self) -> None:
        logger.debug("Shutdown tasks")
        if self._modules:
            for module in self._modules:
                try:
                    await module.shutdown()
                except Exception as e:
                    logger.error("Failed to shutdown module %s: %s", module.name, e, exc_info=True)
                    raise

    async def _startup_managers(self) -> None:
        if self._managers:
            logger.debug("Startup managers")
            for manager in self._managers:
                try:
                    await manager.initialize()
                except Exception as e:
                    logger.error("Failed to start manager %s: %s", manager.__class__.__name__, e, exc_info=True)
                    raise

    async def _shutdown_managers(self) -> None:
        if self._managers:
            logger.debug("Shutdown managers")
            for manager in self._managers:
                try:
                    await manager.dispose()
                except Exception as e:
                    logger.error("Failed to shutdown manager %s: %s", manager.__class__.__name__, e, exc_info=True)
                    raise

    async def __call__(self, scope, receive, send):
        return await self.app(scope, receive, send)