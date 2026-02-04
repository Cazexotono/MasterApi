import asyncio
from abc import ABC, abstractmethod

from typing import Optional
import httpx


class FakeBaseClient(ABC):
    def __init__(
        self,
        api_url: Optional[httpx.URL],
    ) -> None:
        self.api_url = httpx.URL(api_url or "http://localhost:8000")
        self._client: Optional[httpx.AsyncClient] = None
        self._task: Optional[asyncio.Task] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        if self._client:
            await self._client.aclose()
            self._client = None

    def start_loop(self) -> None:
        if self._client is None:
            raise RuntimeError("Cannot start task before entering async context.")
        if self._task is None:
            self._task = asyncio.create_task(self._start_loop_task())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            finally:
                self._task = None

    @abstractmethod
    async def _start_loop_task(self) -> None:
        raise NotImplementedError
