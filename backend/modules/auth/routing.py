import logging
from typing import Optional
from ipaddress import IPv4Address

from pydantic import Base64Str
from user_agents.parsers import UserAgent
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Response, status, HTTPException, Depends, Form

from shared.schemas import JwtAccessPayload
from shared.models import UserAccount
from shared.enum import UserProvider
from shared.depends import get_client_ip_depends, parse_useragent_depends, jwt_validator_depends, database_session_depends
from shared.utils.jwt import issue_refresh, review_tokens_by_jti

from .schemas import FormAuthLogin, FormAuthSignup, FormResetPasswordRequest, FormResetPassword
from .utils import password_hashed, create_user
from .depends import validate_login_form_depends, validate_signup_form_depends

logger = logging.getLogger("Auth Module")



async def login(
    response: Response,
    form_data: FormAuthLogin = Form(),
    real_ip: IPv4Address = Depends(get_client_ip_depends),
    useragent: UserAgent = Depends(parse_useragent_depends),
    db_session: AsyncSession = Depends(database_session_depends),
    user_account: UserAccount = Depends(validate_login_form_depends),
    
) -> None:
    refresh_token, refresh_payload = await issue_refresh(
        db_session=db_session, 
        response=response, 
        sub=user_account.user_id,
        device=useragent.get_device(), 
        remember=form_data.remember
        )
    logger.debug("User %s login in via email", refresh_payload.sub)


async def signup(
    response: Response,
    form_data: FormAuthSignup = Form(),
    useragent: UserAgent = Depends(parse_useragent_depends),
    real_ip: IPv4Address = Depends(get_client_ip_depends),
    db_session: AsyncSession = Depends(database_session_depends),
    user_account: UserAccount = Depends(validate_signup_form_depends),
) -> None:
    try:
        password_hash = password_hashed(password=form_data.password)
        user_db, account_db, user_info_db = await create_user(
            session=db_session,
            provider=UserProvider.email,
            provider_id=form_data.email,
            password_hash=password_hash,
            client_ip=real_ip,
        )
        await issue_refresh(
            db_session=db_session, 
            response=response, 
            sub=user_db.user_id,
            device=useragent.get_device(), 
            remember=form_data.remember 
        )
        logger.debug("User %s(%s) signup in via email", user_info_db.display_name, user_db.user_id,)

    except HTTPException:
        raise

    except Exception as e:
        logger.error("User fail signup in via email: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from e


async def logout(
    response: Response,
    db_session: AsyncSession = Depends(database_session_depends),
    access_payload: Optional[JwtAccessPayload] = Depends(jwt_validator_depends),
    ) -> None:
    if access_payload:
        await review_tokens_by_jti(db_session=db_session, response=response, jti=access_payload.jti)
        logger.debug("User %s logout", access_payload.sub)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

async def reset_password_request(
    request: Request,
    real_ip: IPv4Address = Depends(get_client_ip_depends),
    form_data: FormResetPasswordRequest = Form(),
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

async def reset_password(
    request: Request,
    reset_token: Base64Str,
    real_ip: IPv4Address = Depends(get_client_ip_depends),
    form_data: FormResetPassword = Form(),
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)