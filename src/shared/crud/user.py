from datetime import datetime, timezone
from ipaddress import IPv4Address
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import UserPublicInfo, UserAccount

__all__ = ("read_user_info_by_id", "update_user_info_by_id", "update_user_last_activity")

# Read
async def read_user_info_by_id(session: AsyncSession, user_id: int) -> Optional[UserPublicInfo]:
    return await session.get(UserPublicInfo, user_id)

# Update
async def update_user_info_by_id(session: AsyncSession, user_id: int, data: dict) -> Optional[int]:
    stmt = update(UserPublicInfo).where(UserPublicInfo.user_id == user_id).values(data)
    result = await session.execute(stmt)
    return result.rowcount


async def update_user_last_activity(
    session: AsyncSession, user_id: int, client_ip: IPv4Address
) -> bool:
    result = await session.execute(
        update(UserAccount)
        .where(UserAccount.user_id == user_id)
        .values(last_ip=client_ip, last_login=datetime.now(timezone.utc))
    )
    return result.rowcount > 0