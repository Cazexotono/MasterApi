from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.project_path import secret_path

class SecretSettings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir=str(secret_path))

    rsa_private: SecretStr
    rsa_public: SecretStr
