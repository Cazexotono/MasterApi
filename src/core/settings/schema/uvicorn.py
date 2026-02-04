from pydantic import BaseModel

class UvicornSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000