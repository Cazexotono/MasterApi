from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Response

from core import project
from shared.schemas import JwtRefreshPayload, JwtAccessPayload, JwtAccessToken, JwtRefreshToken

from .provider import create_refresh, create_access
from .crud import create_or_update_refresh_token, delete_refresh_by_jti
from ..cookie import cookie_change, cookie_clear

__all__ = (
    "issue_refresh",
    "issue_access_by_refresh",
    "issue_refresh_and_access_tokens",
    "clear_token_cookie",
    "review_tokens_by_jti",
)

async def issue_refresh(
    db_session: AsyncSession,
    response: Response,
    sub: int,
    device: str,
    remember: bool
    ) -> tuple[JwtRefreshToken, JwtRefreshPayload]:

    refresh_token, refresh_payload = create_refresh(sub=str(sub), iss=project.name, aud=device)
    await create_or_update_refresh_token(
        session=db_session,
        device=device,
        token=refresh_token,
        token_payload=refresh_payload,
    )
    cookie_change(
        response=response,
        key="refresh_token",
        value=refresh_token,
        expire=refresh_payload.exp if remember else None,
    )
    return refresh_token, refresh_payload


async def issue_access_by_refresh(
    response: Response, 
    refresh_payload: JwtRefreshPayload, 
    username: str
    ) -> tuple[JwtAccessToken, JwtAccessPayload]:

    access_token, access_payload = create_access(refresh_payload=refresh_payload, username=username)
    cookie_change(
        response=response,
        key="access_token",
        value=access_token,
        expire=access_payload.exp,
    )
    return access_token, access_payload

async def issue_refresh_and_access_tokens(
    db_session: AsyncSession,
    response: Response,
    sub: int,
    username: str,
    device: str,
    remember: bool,
    ) -> tuple[JwtRefreshToken, JwtRefreshPayload, JwtAccessToken, JwtAccessPayload]:

    refresh_token, refresh_payload = await issue_refresh(db_session=db_session, response=response, sub=sub, device=device, remember=remember)
    access_token, access_payload = await issue_access_by_refresh(response=response, refresh_payload=refresh_payload, username=username)
    return refresh_token, refresh_payload, access_token, access_payload


def clear_token_cookie(response: Response):
    cookie_clear(response, "access_token")
    cookie_clear(response, "refresh_token")


async def review_tokens_by_jti(
    db_session: AsyncSession,
    response: Response,
    jti: str,
    ) -> None:

    await delete_refresh_by_jti(session=db_session, jti=jti)
    clear_token_cookie(response=response)
