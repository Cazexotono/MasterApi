from typing import Optional
from ipaddress import IPv4Address

from pydantic import BaseModel, Field

__all__ = ['ServerCreateFormRequest']

class ServerCreateFormRequest(BaseModel):
    display_name: str = Field(max_length=64)
    description: Optional[str] = Field(max_length=2048)
    host: Optional[IPv4Address] = Field(default=None)
    main_port: int = Field(ge=0, le=65535)