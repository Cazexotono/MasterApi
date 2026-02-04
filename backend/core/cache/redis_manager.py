from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from pydantic import RedisDsn
import redis.asyncio as redis

from shared.interfaces import BaseManager

class RedisManager(BaseManager):
    def __init__(
            self,
            redis_url: RedisDsn,
            ) -> None:

        self._url: RedisDsn = redis_url

        self._cache_pool = redis.ConnectionPool.from_url(
            self._url.encoded_string(),
            max_connections=20,
            decode_responses=True,
        )
    
    async def initialize(self) -> None:
        try:
            await self.health_check(auto_error=True)
        except:
            raise

    async def dispose(self) -> None:
        pass

    async def health_check(self, auto_error: bool = False) -> bool:
        try:
            async with self.get_client_context() as client:
                await client.ping()
            return True
        except Exception:
            if auto_error:
                raise
            return False

    @asynccontextmanager
    async def get_client_context(self):
        client = redis.Redis(connection_pool=self._cache_pool)
        try:
            yield client
        except:
            raise
        finally:
            await client.close()


    async def get_client_depends(self) -> AsyncGenerator[redis.Redis]:
        async with self.get_client_context() as client:
            yield client