from typing import Optional
from ipaddress import IPv4Address

from pydantic import SecretBytes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import User, UserAccount, UserPublicInfo
from shared.enum import UserProvider


__all__ = (
    "create_user",
    "read_user_account_by_provider_id",
)

# User
# Create
async def create_user(
    session: AsyncSession,
    provider: UserProvider,
    provider_id: str,
    password_hash: Optional[SecretBytes],
    client_ip: IPv4Address,
) -> tuple[User, UserAccount, UserPublicInfo]:
    
    user = User()
    session.add(user)
    await session.flush()

    account = UserAccount(
        user_id=user.user_id,
        provider=provider,
        provider_id=provider_id,
        password_hash=password_hash,
        reg_ip=client_ip,
    )

    info = UserPublicInfo(
        user_id=user.user_id,
        display_name=provider_id.split("@")[0] if "@" in provider_id else provider_id,
    )
    session.add_all([account, info])
    await session.flush()

    return user, account, info


# Read
async def read_user_account_by_provider_id(
    session: AsyncSession, provider: UserProvider, provider_id: str
) -> Optional[UserAccount]:
    return await session.scalar(
        select(UserAccount)
        .where(UserAccount.provider == provider, UserAccount.provider_id == provider_id)
    )


