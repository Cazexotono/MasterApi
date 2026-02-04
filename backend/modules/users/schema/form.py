from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

__all__ = (
    "FormUpdatePublicInfo", 
    )

form_model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)

class FormUpdatePublicInfo(BaseModel):
    model_config = form_model_config

    # Как-то обновлять только определёные данные
    display_name: Optional[str] = Field(default=None, min_length=3, max_length=64)
    avatar: Optional[str] = Field(default=None, max_length=1024)
    description: Optional[str] = Field(default=None, max_length=1024)

