import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pydantic import PostgresDsn

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from shared.interfaces import BaseManager

logger = logging.getLogger("app")

class SqlAlchemyManager(BaseManager):
    def __init__(
            self, 
            database_url: PostgresDsn
            ) -> None:

        self._url: PostgresDsn = database_url

        self._async_engine: AsyncEngine = create_async_engine(
            url=self._url.encoded_string(),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=15,
            max_overflow=20,
        )

        self._async_sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._async_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def initialize(self) -> None:
        try:
            await self.health_check(auto_error=True)
        except SQLAlchemyError:
            raise
        except:
            raise

    async def dispose(self) -> None:
        if self._async_engine:
            await self._async_engine.dispose()

    @asynccontextmanager
    async def get_session_context(self):
        session = self._async_sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
        finally:
            await session.close()


    async def get_session_depends(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.get_session_context() as session:
            yield session


    async def health_check(self, auto_error: bool = False) -> bool:
        try:
            async with self._async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            if auto_error:
                raise
            return False