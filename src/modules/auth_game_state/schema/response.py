from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


__all__ = ("UserGameData",)


class UserGameData(BaseModel):
    token: str
    api_id: int = Field(alias="masterApiId")
    username: Optional[str] = Field(alias="discordUsername", default=None)
    discriminator: Optional[str] = Field(alias="discordDiscriminator", default=None)
    avatar: Optional[str] = Field(alias="discordAvatar", default=None)
    
    model_config = ConfigDict(populate_by_name=False, alias_generator=None)
