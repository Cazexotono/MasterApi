from typing import Optional
from pydantic import BaseModel, AnyHttpUrl, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PyprojectTomlConfigSettingsSource,
)


class PyprojectBase(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            PyprojectTomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class ProjectUrlsSchema(BaseModel):
    homepage: Optional[AnyHttpUrl] = Field(default=None)
    documentation: Optional[AnyHttpUrl] = Field(default=None)
    repository: Optional[AnyHttpUrl] = Field(default=None)
    issues: Optional[AnyHttpUrl] = Field(default=None)
    changelog: Optional[AnyHttpUrl] = Field(default=None)


class ProjectSchema(PyprojectBase):
    model_config = SettingsConfigDict(extra="allow", pyproject_toml_depth=2, pyproject_toml_table_header=("project",))

    name: str = Field(default="Master Api")
    version: str = Field(default="0.0.0")
    description: str = Field(default="Unofficial Master API for the multiplayer mod for TESV: Skyrim")
    urls: Optional[ProjectUrlsSchema] = Field(default=None)
