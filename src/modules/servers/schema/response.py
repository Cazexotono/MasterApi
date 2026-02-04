from typing import Optional

from uuid import UUID
from ipaddress import IPv4Address

from pydantic import BaseModel, Field

from .common import ServerInfo

__all__ = ['ServersListResponse', 'ServerConnectResponse']



class ServersListResponse(BaseModel):
    online_servers: Optional[int] = Field(default=None, ge=0, )
    online_players: Optional[int] = Field(default=None, ge=0, )
    servers: dict[UUID, ServerInfo] = Field(default={})


class ServerConnectResponse(BaseModel):
    key: UUID
    host: IPv4Address
    port: int = Field(ge=1024, le=65535)