
from pydantic import BaseModel, ConfigDict, SecretStr, EmailStr, Field


__all__ = (
    "FormAuthLogin", 
    "FormAuthSignup",
    "FormResetPasswordRequest",
    "FormResetPassword",
    )

form_model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)

class FormAuthLogin(BaseModel):
    model_config = form_model_config

    email: EmailStr = Field()
    password: SecretStr = Field()
    remember: bool = Field(default=False)


class FormAuthSignup(BaseModel):
    model_config = form_model_config

    email: EmailStr = Field()
    password: SecretStr = Field()
    password_repeat: SecretStr = Field()
    remember: bool = Field(default=False)

class FormResetPasswordRequest(BaseModel):
    model_config = form_model_config

    email: EmailStr = Field()


class FormResetPassword(BaseModel):
    model_config = form_model_config

    password: SecretStr = Field()
    password_repeat: SecretStr = Field()