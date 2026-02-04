import asyncio
import logging
from typing import Optional
import time
from uuid import UUID

from shared.interfaces import BaseTask
from ..schema import ServerStorage

logger = logging.getLogger("app")

class ServerManagementTask(BaseTask):
    def __init__(self, expires: float = 7.5) -> None:
        super().__init__()
        self._servers_expires: dict[UUID, float] = {}
        self._servers_online: dict[UUID, ServerStorage] = {}
        self._expire = expires

    async def add_server(self, server_uuid: UUID, storage: ServerStorage) -> None:
        async with self._lock:
            self._servers_expires[server_uuid] = time.time() + self._expire
            self._servers_online[server_uuid] = storage
    
    async def update_server(self, server_uuid: UUID, online: int) -> None:
        async with self._lock:
            self._servers_expires[server_uuid] = time.time() + self._expire
            self._servers_online[server_uuid].online = online


    async def remove_server(self, server_uuid: UUID) -> None:
        async with self._lock:
            self._remove_server_unsafe(server_uuid)

    async def get_online_servers(self) -> dict[UUID, ServerStorage]:
        async with self._lock:
            return self._servers_online.copy()

    async def get_server(self, server_uuid: UUID) -> Optional[ServerStorage]:
        async with self._lock:
            return self._servers_online.get(server_uuid, None)

    async def _run(self) -> None:
        try:
            while True:
                async with self._lock:
                    now = time.time()
                    for server, expire_at in list(self._servers_expires.items()):
                        if expire_at < now:
                            self._remove_server_unsafe(server)
                await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            pass

    def _remove_server_unsafe(self, server: UUID) -> None:
        self._servers_expires.pop(server, None)
        self._servers_online.pop(server, None)