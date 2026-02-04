import redis
from typing import Optional
from ulid import ULID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException, status, Depends, Query, Form
from fastapi.responses import RedirectResponse

from shared.enum import StateStatus
from shared.utils import cookie_change
from shared.depends import redis_client_depends, database_session_depends, jwt_validator_depends
from shared.schemas import JwtAccessPayload
from shared.crud import read_user_info_by_id

from .schema import UserGameData, FormChangeState

state_query = Query(pattern=r"^[a-f0-9]{64}$", default=None, description="Token for communication between the game client and the API user.")

async def create_status_tracking(
    request: Request,
    redis_client: redis.Redis = Depends(redis_client_depends),
    access_payload: Optional[JwtAccessPayload] = Depends(jwt_validator_depends),
    state: str = state_query,
    ):
    if access_payload:
        redirect = RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)
    else:
        # Сразу к форме
        redirect = RedirectResponse(url="/redoc", status_code=status.HTTP_302_FOUND)
    state_cookie = request.cookies.get("state")
    if not state_cookie or state != state_cookie:
        cookie_change(response=redirect, key="state", value=state, expire=None)
        await redis_client.set(name=f"state:{state}", value=str(StateStatus.none), ex=180)
    return redirect


async def get_state_status(
    state: str = state_query,
    redis_client: redis.Redis = Depends(redis_client_depends),
    db_session: AsyncSession = Depends(database_session_depends)
    ) -> UserGameData:
    state_status = await redis_client.get(name=f"state:{state}")
    match state_status:
        case StateStatus.none:
            await redis_client.expire(f"state:{state}", 180)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        case StateStatus.error:
            await redis_client.delete(f"state:{state}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="State error")
        case StateStatus.denied:
            await redis_client.delete(f"state:{state}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="State denied")
        case StateStatus.access:
            user_id = await redis_client.get(name=f"state_user:{state}")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="State expire")
            user_id = int(user_id)
            await redis_client.delete(f"state_user:{state}")
            await redis_client.delete(f"state:{state}")
            user_data = await read_user_info_by_id(session=db_session, user_id=user_id)
            if not user_data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            session = UserGameData(
                token=str(ULID),
                masterApiId=user_id,
                discordUsername=user_data.display_name,
                discordDiscriminator=user_data.display_name + f"#{user_id}",
                discordAvatar=user_data.avatar,
            )
            await redis_client.set(name=f"session_token:{session.token}", value=user_id, ex=180)
            return session
        case _:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="State expire")


async def update_status_tracking(
    request: Request,
    access_payload: Optional[JwtAccessPayload] = Depends(jwt_validator_depends),
    redis_client: redis.Redis = Depends(redis_client_depends),
    form_data: FormChangeState = Form(),
    ):
    state = request.cookies.get("state", None)
    if not state:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    state_status = await redis_client.get(name=f"state:{state}")
    if not access_payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if state_status in StateStatus.none:
        match form_data.status:
            case StateStatus.access:
                await redis_client.set(name=f"state_user:{state}", value=access_payload.sub, ex=300)
                await redis_client.set(name=f"state:{state}", value=StateStatus.access, ex=300)
            case StateStatus.denied:
                await redis_client.set(name=f"state:{state}", value=StateStatus.denied, ex=300)
            case _:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
