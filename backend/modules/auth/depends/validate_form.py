import re

from fastapi import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from shared.enum import UserProvider
from shared.depends import database_session_depends
from ..schemas import FormAuthLogin, FormAuthSignup, UserAccountModel
from ..utils import read_user_account_by_provider_id, password_verify
from ..errors import AuthError, AuthErrorCode 

__all__ = ("validate_signup_form_depends", "validate_login_form_depends",)

DOMAIN_BLACK_LIST = ("tempmail.com",) 

async def validate_signup_form_depends(
    form_data: FormAuthSignup = Form(),
    db_session: AsyncSession = Depends(database_session_depends),
    ) -> None:
    try:
        email_domain = form_data.email.split("@")[-1].lower()
        if email_domain in DOMAIN_BLACK_LIST:
            raise AuthError(detail="Email domain blocked", error_code=AuthErrorCode.EMAIL_DOMAIN_BLOCKED)

        password = form_data.password.get_secret_value()
        password_len = len(password)

        if password != form_data.password_repeat.get_secret_value():
            raise AuthError(detail="Password not match repeat", error_code=AuthErrorCode.PASSWORD_NOT_MATCH_REPEAT)

        if not 8 < password_len:
            raise AuthError(detail="Password too short", error_code=AuthErrorCode.PASSWORD_TOO_SHORT)
        if not password_len < 32:
            raise AuthError(detail="Password too long", error_code=AuthErrorCode.PASSWORD_TOO_LONG)
        if not re.search(r"[A-Z]", password):
            raise AuthError(detail="Password missing uppercase", error_code=AuthErrorCode.PASSWORD_MISSING_UPPERCASE)
        if not re.search(r"[a-z]", password):
            raise AuthError(detail="Password missing lowercase", error_code=AuthErrorCode.PASSWORD_MISSING_LOWERCASE)
        if not re.search(r"\d", password):
            raise AuthError(detail="Password missing digit", error_code=AuthErrorCode.PASSWORD_MISSING_DIGIT)
        account_db = await read_user_account_by_provider_id(session=db_session, provider=UserProvider.email, provider_id=form_data.email)
        if account_db:
            raise AuthError(detail="Email already exists", error_code=AuthErrorCode.EMAIL_ALREADY_EXISTS)
    except AuthError:
        raise


async def validate_login_form_depends(
    form_data: FormAuthLogin = Form(),
    db_session: AsyncSession = Depends(database_session_depends),
    ) -> UserAccountModel:
    try:
        account_db = await read_user_account_by_provider_id(session=db_session, provider=UserProvider.email, provider_id=form_data.email)
        if not account_db:
            raise AuthError(detail="Email not found", error_code=AuthErrorCode.EMAIL_NOT_FOUND)
        if not account_db.password_hash:
            raise AuthError(detail="Password not found", error_code=AuthErrorCode.PASSWORD_INCORRECT) 
        if not password_verify(form_data.password, account_db.password_hash):
            raise AuthError(detail="Password incorrect", error_code=AuthErrorCode.PASSWORD_INCORRECT) 
        return UserAccountModel.model_validate(account_db)

    except AuthError:
        raise AuthError(detail="User or password invalid", error_code=AuthErrorCode.INVALID_CREDENTIALS)
