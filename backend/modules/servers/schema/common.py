from pydantic import BaseModel, Field, ByteSize

__all__ = ['ServerModsManifest', 'ServerInfo']

class ServerMod(BaseModel):
    crc32: int = Field(repr=False)
    filename: str = Field(max_length=64)
    size: ByteSize

class ServerModsManifest(BaseModel):
    mods: list[ServerMod]
    version: int = Field(alias="versionMajor", repr=False)
    load_order: list[str] = Field(alias="loadOrder")

class ServerInfo(BaseModel):
    name: str = Field(max_length=32)
    online: int = Field(ge=0, le=1500)
    max_players: int = Field(alias="maxPlayers", ge=0, le=1500)
