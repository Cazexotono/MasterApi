from pydantic import BaseModel, ConfigDict

from shared.enum.status import StateStatus

__all__ = ("FormChangeState",)


form_model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)

class FormChangeState(BaseModel):
    model_config = form_model_config

    status: StateStatus
