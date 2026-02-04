from pydantic import BaseModel,PostgresDsn, Field
from typing import Optional


class DatabaseSettings(BaseModel):
    db_url: Optional[PostgresDsn] = Field(default=None, description="SQLAlchemy-compatible database PostgresDsn")
    pool_size: int = Field(default=20, ge=1, description="Size of the connection pool")
    max_overflow: int = Field(default=10, ge=0, description="Max overflow connections")
