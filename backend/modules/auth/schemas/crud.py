from ipaddress import IPv4Address
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from shared.enum import UserProvider, AccessStatus

crud_config_dict = ConfigDict(from_attributes=True, extra="ignore", frozen=True)

__all__ = ("ApiUserModel", "UserAccountModel", "UserTokenModel", "UserModel",)


class ApiUserModel(BaseModel):
    model_config = crud_config_dict

    api_id: int
    username: str
    avatar: str | None = None
    description: str | None = None
    status: AccessStatus
    status_timestamp: datetime | None = None
    status_description: str | None = None


class UserAccountModel(BaseModel):
    model_config = crud_config_dict

    user_id: int
    provider: UserProvider
    provider_id: str
    verified: bool
    reg_ip: IPv4Address
    last_ip: Optional[IPv4Address]
    last_login: Optional[datetime]


class UserTokenModel(BaseModel):
    model_config = crud_config_dict

    device: str
    jti: str
    token: str
    expires_at: datetime


class UserModel(BaseModel):
    model_config = crud_config_dict

    user: ApiUserModel
    account: list[UserAccountModel]
    token_refresh: list[UserTokenModel]

