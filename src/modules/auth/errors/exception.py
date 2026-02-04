from fastapi import status
from .error_code import AuthErrorCode

class AuthError(Exception):
    def __init__(
        self, 
        detail: str,
        error_code: AuthErrorCode,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,

        ) -> None:
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)
