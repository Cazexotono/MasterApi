from typing import Optional
from ipaddress import IPv4Address
from datetime import datetime, timezone

from pydantic import SecretBytes
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import User, UserPublicInfo
from shared.enum import UserProvider

__all__ = ("read_user_info_by_id",)

async def read_user_info_by_id(session: AsyncSession, user_id: int) -> Optional[UserPublicInfo]:
    return await session.get(UserPublicInfo, user_id)