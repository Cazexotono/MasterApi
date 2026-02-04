from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


from shared.project_path import root_path
from shared.enum import Environment

from .schema import UvicornSettings, DatabaseSettings, RedisSettings, ProjectSchema, SecretSettings

class ApiSettings(BaseSettings, UvicornSettings):
    model_config = SettingsConfigDict(
        frozen=True, 
        case_sensitive=False,
        env_prefix="API__",
        env_nested_delimiter='__',
        env_file=[root_path/'.env.template', root_path/'.env'],
        env_file_encoding="utf-8",
        env_ignore_empty=True
    )
    environment: Environment = Environment.dev
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
