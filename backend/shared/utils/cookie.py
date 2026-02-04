from typing import Optional
from time import time

from fastapi import Response

__all__ = ("cookie_change", "cookie_clear",)

def cookie_change(
    response: Response, key: str, value: str, expire: Optional[float] = None
) -> None:
    exp = None
    max_age = None

    if expire:
        exp = int(expire)
        max_age = max(0, int(expire - time()))

    response.set_cookie(
        key=key,
        value=value,
        secure=True,
        httponly=True,
        samesite="lax",
        max_age=max_age,
        expires=exp,
        )


def cookie_clear(response: Response, key: str) -> None:
    response.delete_cookie(
        key=key,
        secure=True,
        httponly=True,
        samesite="lax",
    )
