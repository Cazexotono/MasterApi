from ipaddress import IPv4Address

from pydantic import BaseModel, Field

from shared.enum.server import ServerGamemode

from . import ServerModsManifest

__all__ = ['ServerStorage']

class ServerStorage(BaseModel):
    display_name: str = Field(max_length=64)
    host: IPv4Address
    port: int = Field(ge=1024, le=65535)
    online: int = Field(ge=0, le=1500)
    max_players: int = Field(ge=0, le=1500)
    gamemode: ServerGamemode
    manifest: ServerModsManifest