import logging
from typing import Optional
from jwt.exceptions import InvalidTokenError, InvalidJTIError, PyJWTError

from fastapi import Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents.parsers import UserAgent

from core import project
from shared.schemas import (
    JwtAccessPayload,
    JwtAccessToken,
    JwtRefreshPayload,
    JwtRefreshToken,
)
from shared.utils.jwt import (
    jwt_decode,
    need_for_reissue,
    clear_token_cookie,
    issue_refresh_and_access_tokens,
    issue_access_by_refresh,
    read_refresh_token_by_jti,
    get_display_name_by_user_id,
)
from . import parse_useragent_depends, database_session_depends

logger = logging.getLogger("console")

__all__ = ("jwt_validator_depends",)

async def jwt_validator_depends(
    request: Request,
    response: Response,
    user_agent: UserAgent = Depends(parse_useragent_depends),
    db_session: AsyncSession = Depends(database_session_depends),
) -> Optional[JwtAccessPayload]:
    try:
        refresh_token: Optional[JwtRefreshToken] = request.cookies.get(
            "refresh_token", None
        )
        access_token: Optional[JwtAccessToken] = request.cookies.get(
            "access_token", None
        )
        if not access_token and not refresh_token:
            access_payload = None
        elif access_token and not refresh_token:
            clear_token_cookie(response=response)
            access_payload = None
        elif refresh_token:
            aud = user_agent.get_device()
            refresh_payload = jwt_decode(token=refresh_token, aud=aud, iss=project.name)
            if not isinstance(refresh_payload, JwtRefreshPayload):
                raise InvalidTokenError("Token type error")
            db_refresh_token = await read_refresh_token_by_jti(
                session=db_session, jti=refresh_payload.jti
            )
            if not db_refresh_token:
                raise InvalidJTIError("Token not found in db")
            if refresh_token != db_refresh_token.token:
                raise InvalidTokenError(
                    "The token differs from the one in the database"
                )
            username = await get_display_name_by_user_id(
                session=db_session, user_id=db_refresh_token.account_user_id
            )
            if need_for_reissue(refresh_payload):
                (
                    refresh_token,
                    refresh_payload,
                    access_token,
                    access_payload,
                ) = await issue_refresh_and_access_tokens(
                    db_session=db_session,
                    sub=db_refresh_token.account_user_id,
                    username=username,
                    response=response,
                    device=aud,
                    remember=True,
                )
            elif not access_token:
                access_token, access_payload = await issue_access_by_refresh(
                    response=response,
                    refresh_payload=refresh_payload,
                    username=username,
                )
            else:
                access_payload = jwt_decode(access_token, aud=aud, iss=project.name)
                if not isinstance(access_payload, JwtAccessPayload):
                    raise InvalidTokenError("Token type error")
                if refresh_payload.jti != access_payload.jti:
                    raise InvalidJTIError("Tiken jti does not match")
                if need_for_reissue(access_payload):
                    access_token, access_payload = await issue_access_by_refresh(
                        response=response,
                        refresh_payload=refresh_payload,
                        username=username,
                    )
    except PyJWTError:
        clear_token_cookie(response=response)
        return None
    return access_payload