from typing import Union, Literal, TypeAlias

from ulid import ULID
from pydantic import BaseModel, ConfigDict, Field, field_validator


__all__ = (
    "TokenTypeStr",
    "JwtRefreshToken",
    "JwtAccessToken",
    "JwtRefreshPayload",
    "JwtAccessPayload",
)

TokenTypeStr = Literal["access", "refresh"]
JwtRefreshToken: TypeAlias = str
JwtAccessToken: TypeAlias = str

jwt_model_config = ConfigDict(extra="forbid", frozen=True)


class JwtBasePayload(BaseModel):
    model_config = jwt_model_config

    type: TokenTypeStr
    sub: str
    jti: str
    iss: str
    aud: str
    iat: float
    nbf: float 
    exp: float

    @field_validator("sub", mode="before")
    def convert_sub_to_str(cls, value: Union[int, str]) -> str:
        return str(value)


class JwtRefreshPayload(JwtBasePayload):
    type: Literal["refresh"] = Field(default="refresh")
    jti: str = Field(default_factory=lambda: str(ULID()))


class JwtAccessPayload(JwtBasePayload):
    type: Literal["access"] = Field(default="access")
    uname: str = Field(min_length=3, max_length=64)

