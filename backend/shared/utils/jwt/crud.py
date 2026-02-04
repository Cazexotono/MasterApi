from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import RefreshToken, UserPublicInfo
from shared.schemas import JwtRefreshPayload

__all__ = (
    "create_or_update_refresh_token",
    "read_refresh_token_by_jti",
    "get_display_name_by_user_id",
    "delete_refresh_by_user_id_and_device",
    "delete_refresh_by_jti",
    "delete_refresh_all_by_user_id",
    "delete_refresh_expired",
)

# Tokens
# Create
async def create_or_update_refresh_token(
    session: AsyncSession, token: str, token_payload: JwtRefreshPayload, device: str
) -> RefreshToken:
    token_obj = RefreshToken(
        jti=token_payload.jti,
        account_user_id=int(token_payload.sub),
        device=device,
        token=token,
        expires_at=datetime.fromtimestamp(timestamp=token_payload.exp, tz=timezone.utc)
        )
    merged_obj = await session.merge(token_obj)
    await session.flush()
    return merged_obj

# Read
async def read_refresh_token_by_jti(session: AsyncSession, jti: str) -> Optional[RefreshToken]:
    stmt = select(RefreshToken).where(RefreshToken.jti==jti)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_display_name_by_user_id(session: AsyncSession, user_id: int) -> str:
    stmt = select(UserPublicInfo.display_name).where(UserPublicInfo.user_id == user_id)
    result = await session.execute(stmt)
    row = result.first()
    if row is None:
        raise ValueError("User public info not found")
    return row[0]

# Delete
async def delete_refresh_by_user_id_and_device(
    session: AsyncSession, account_user_id: int, device: str
) -> bool:
    result = await session.execute(
        delete(RefreshToken).where(
            RefreshToken.account_user_id == account_user_id, RefreshToken.device == device
        )
    )
    return result.rowcount > 0


async def delete_refresh_by_jti(session: AsyncSession, jti: str) -> bool:
    result = await session.execute(
        delete(RefreshToken).where(RefreshToken.jti == jti)
    )
    return result.rowcount > 0


async def delete_refresh_all_by_user_id(session: AsyncSession, account_user_id: int) -> int:
    result = await session.execute(
        delete(RefreshToken).where(RefreshToken.account_user_id == account_user_id)
    )
    return result.rowcount


async def delete_refresh_expired(session: AsyncSession) -> int:
    result = await session.execute(
        delete(RefreshToken).where(
            RefreshToken.expires_at <= datetime.now(timezone.utc)
        )
    )
    return result.rowcount
