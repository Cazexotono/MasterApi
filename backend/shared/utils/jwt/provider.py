from typing import Literal, Union
from time import time

import jwt

from core import secret
from shared.schemas.jwt import JwtRefreshPayload, JwtAccessPayload

__all__ = (
    "jwt_encode",
    "jwt_decode",
    "create_refresh",
    "create_access",
    "need_for_reissue",
)

algorithm: Literal["RS256"] = "RS256"
refresh_expire: float  = 1209600
access_expire: float = 900
reissue: float = 0.25
public_key = secret.rsa_public
private_key = secret.rsa_private


def jwt_encode(payload: Union[JwtRefreshPayload, JwtAccessPayload]) -> str:
    return jwt.encode(
        payload=payload.model_dump(mode="json"),
        algorithm=algorithm,
        key=private_key.get_secret_value(),
    )


def jwt_decode(token: str, iss: str, aud: str) -> Union[JwtRefreshPayload, JwtAccessPayload]:
    decoded = jwt.decode_complete(
        jwt=token,
        key=public_key.get_secret_value(),
        algorithms=[algorithm],
        audience=aud,
        issuer=iss,
        leeway=5,
        options={
            "require": ["type", "sub", "jti", "iat", "nbf", "exp", "aud", "iss"], 
            "verify_exp": True, 
            "verify_nbf": True, 
            "verify_aud": True,
            "verify_iss": True,
            },
    )
    payload_class = get_payload_class(decoded["payload"]["type"])
    return payload_class.model_validate(decoded["payload"])


def create_refresh( sub: str, iss: str, aud: str) -> tuple[str, JwtRefreshPayload]:
    time_now = time()
    refresh_payload = JwtRefreshPayload(
        sub=sub, 
        iss=iss,
        exp=time_now + refresh_expire,
        aud=aud,
        iat= time_now,
        nbf=time_now
        )
    refresh_token = jwt_encode(refresh_payload)
    return refresh_token, refresh_payload


def create_access(
    refresh_payload: JwtRefreshPayload, 
    username: str
) -> tuple[str, JwtAccessPayload]:
    time_now = time()
    access_payload = JwtAccessPayload(
        sub=refresh_payload.sub,
        jti=refresh_payload.jti,
        iss=refresh_payload.iss,
        exp=time_now + access_expire,
        uname=username,
        aud=refresh_payload.aud,
        iat= time_now,
        nbf=time_now
    )
    access_token = jwt_encode(access_payload)
    return access_token, access_payload

def get_payload_class(token_type: str):
    if token_type == "refresh":
        return JwtRefreshPayload
    elif token_type == "access":
        return JwtAccessPayload
    else:
        raise jwt.InvalidTokenError(f"Unsupported token type: {token_type}")

def need_for_reissue( token_payload: Union[JwtRefreshPayload, JwtAccessPayload]) -> bool:
    buffer = (token_payload.exp - token_payload.iat) * reissue
    return (token_payload.exp - buffer) < time()

