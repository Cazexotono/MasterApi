from typing import Optional
from ipaddress import IPv4Address
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from shared.enum import ServerGamemode, AccessStatus


__all__ = ['ServerPublicInfoModel', 'ServerModel']


crud_config_dict = ConfigDict(from_attributes=True, extra="ignore")


class ServerPublicInfoModel(BaseModel):
    model_config = crud_config_dict
    
    display_name: str
    description: Optional[str]
    host: IPv4Address
    main_port: int
    icon: Optional[str]
    locale: Optional[str]
    gamemode_type: ServerGamemode
    game_version: Optional[str]
    visible: bool
    links: Optional[dict]


class ServerModel(BaseModel):
    model_config = crud_config_dict
    
    uuid: UUID
    owner_user_id: int
    status: AccessStatus
    info: ServerPublicInfoModel