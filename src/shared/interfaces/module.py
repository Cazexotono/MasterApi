import logging
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import APIRouter, FastAPI

from shared.enum import Environment
from shared.logs import console_module_handler
from .task import BaseTask

logger = logging.getLogger("console")

class BaseModule(ABC):
    name: str
    version: str
    description: str
    tags: Optional[str]
    dependencies: Optional[list[type["BaseModule"]]]
    prefix: Optional[str]

    def __init__(self) -> None:
        self.router: Optional[APIRouter] = None
        self.tasks: list[BaseTask] = []

    def __str__(self) -> str:
        return f"{self.name}: {self.version}"

    def _setup(self, environment: Environment, app: FastAPI) -> None:
        self.router = APIRouter(prefix=self.prefix or "", tags=[self.tags] if self.tags else None)
        self._logger(environment=environment)
        self.setup_module(environment=environment, app=app)

    async def startup(self) -> None:
        for task in self.tasks:
            await task.start_task()
            logger.debug("[%s] Starting task: %s", self.name, task.__class__.__name__)


    async def shutdown(self) -> None:
        for task in self.tasks:
            await task.stop_task()
            logger.debug("[%s] Shutdown task: %s", self.name, task.__class__.__name__)

    def _logger(self, environment: Environment):
        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(console_module_handler)
        self.logger.propagate = False
        match environment:
            case Environment.dev:
                self.logger.setLevel(logging.DEBUG)
            case Environment.staging:
                self.logger.setLevel(logging.INFO)
            case Environment.production:
                self.logger.setLevel(logging.WARNING)


    @abstractmethod
    def setup_module(self, environment: Environment, app: FastAPI) -> None:
        """A method for declaring routers, middleware, replacing dependencies, adding tasks, and performing other actions on a FastApi application.

        Args:
            environment (Environment): _description_

        Raises:
            NotImplementedError: _description_
        """
        
        raise NotImplementedError
    
