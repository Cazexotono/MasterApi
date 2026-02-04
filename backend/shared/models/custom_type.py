from typing import Optional
from ulid import ULID

from sqlalchemy.types import TypeDecorator, LargeBinary, VARCHAR
from pydantic import SecretBytes


__all__ = ("SecretByteType","ULIDType",)

class SecretByteType(TypeDecorator):
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, SecretBytes):
            return value.get_secret_value()
        if isinstance(value, bytes):
            return value
        raise TypeError("Expected SecretBytes or bytes")

    def process_result_value(self, value: Optional[bytes], dialect) -> Optional[SecretBytes]:
        if value is not None:
            return SecretBytes(value)
        return value

class ULIDType(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ULID.from_str(value) 