
import asyncio
import random
from uuid import UUID
from typing import Optional

import httpx
from mimesis import Generic

from .fake_base_client import FakeBaseClient

from src.modules.servers.schema.common import ServerInfo


class FakeServer(FakeBaseClient):
    def __init__(
        self,
        server_uuid: Optional[UUID],
        name: Optional[str],
        current_online: Optional[int],
        max_online: Optional[int],
        api_url: Optional[httpx.URL],
    ) -> None:
        super().__init__(api_url)

        generic = Generic()
        self.uuid = server_uuid or UUID()
        self.name = name or f"{generic.text.title()} {generic.text.word()}"
        self.max_online = max_online or 1000
        self.current_online = current_online or random.randint(0, self.max_online)

    async def _start_loop_task(self) -> None:
        try:
            if self._client is None:
                raise RuntimeError("HTTP client not initialized")
            while True:
                delta = random.randint(-3, 3)
                new_online = self.current_online + delta
                self.current_online = max(0, min(self.max_online, new_online))
                content = ServerInfo(
                    name=self.name,
                    online=self.current_online,
                    maxPlayers=self.max_online,
                )
                await self.send_heartbeat(content=content)
                await asyncio.sleep(5.0)
        except asyncio.CancelledError:
            pass

    async def send_heartbeat(self, content: ServerInfo) -> httpx.Response:
        if self._client is None:
            raise RuntimeError("HTTP client not initialized")
        url = self.api_url.join(f"/api/servers/{self.uuid}")
        response = await self._client.post(
            url = url,
            content=content.model_dump_json(),
        )
        response.raise_for_status()
        return response

    async def get_user_session(self, session_token: str):
        if self._client is None:
            raise RuntimeError("HTTP client not initialized")
        url = self.api_url.join(f"/api/servers/{self.uuid}/sessions/{session_token}")
        response = await self._client.get(url = url)
        response.raise_for_status()
        return response
