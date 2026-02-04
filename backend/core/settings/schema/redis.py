from pydantic import BaseModel, RedisDsn, Field
from typing import Optional


class RedisSettings(BaseModel):
    cache_url: Optional[RedisDsn] = Field(default=None, description="Direct Redis URL (e.g., redis://:password@localhost:6379/0)")
    max_connections: Optional[int] = Field(default=10, ge=1, description="Maximum number of connections in pool")