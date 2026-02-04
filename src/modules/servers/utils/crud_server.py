from ipaddress import IPv4Address
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from shared.models import Server, ServerPublicInfo, GameSession
from ..schema import ServerCreateFormRequest

__all__ = [
    "create_server_by_form",
    "read_server_by_UUID",
    "create_game_session",
    'read_game_session_by_token'
]

async def create_server_by_form(
    session: AsyncSession, owner_user_id: int, form_data: ServerCreateFormRequest
) -> tuple[Server, ServerPublicInfo]:
    server = Server(owner_user_id=owner_user_id)
    session.add(server)
    await session.flush()

    info = ServerPublicInfo(server_uuid=server.uuid, **form_data.model_dump())
    session.add(info)
    await session.flush()

    return server, info



async def read_server_by_UUID(
    session: AsyncSession, server_uuid: UUID) -> Optional[Server]:
    server = await session.scalar(
        select(Server)
        .options(joinedload(Server.info))
        .where(Server.uuid == server_uuid)
    )
    return server

# Game Session
# Create
async def create_game_session(
    session: AsyncSession,
    user_id: int,
    server_uuid: UUID, 
    session_token: str,
    user_ip: IPv4Address
) -> GameSession:
    game_session = GameSession(
        session_id=ULID(),
        user_id=user_id,
        server_uuid=server_uuid,
        session_token=session_token,
        reg_ip=user_ip
    )
    session.add(game_session)
    await session.flush()
    return game_session

async def read_game_session_by_token(session: AsyncSession, session_token: str)->Optional[GameSession]:
    return await session.scalar(
        select(GameSession)
        .where(GameSession.session_token == session_token)
    )
