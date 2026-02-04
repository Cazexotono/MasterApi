import asyncio
from abc import ABC, abstractmethod
from typing import Optional

class BaseTask(ABC):
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task] = None
    
    async def start_task(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop_task(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                    pass
            finally:
                self._task = None
    
    @abstractmethod
    async def _run(self) -> None:
        raise NotImplementedError