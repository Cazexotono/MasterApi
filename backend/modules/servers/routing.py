import secrets
from typing import Optional
from uuid import UUID
from ipaddress import IPv4Address

import httpx
from fastapi import HTTPException, status, Form, Header, Depends
import redis
from sqlalchemy.ext.asyncio import AsyncSession

from shared.depends import get_client_ip_depends, database_session_depends, redis_client_depends
from shared.schemas import JwtAccessPayload
from shared.depends import jwt_validator_depends
from .schema import (
    ServersListResponse,
    ServerInfo,
    ServerConnectResponse,
    ServerCreateFormRequest,
    ServerStorage,
    ServerModsManifest,
    ServerModel,
)
from .utils import (
    ServerManagementTask,
    GetServerDepends,
    create_game_session,
    create_server_by_form,
    read_game_session_by_token
)

server_manager_task = ServerManagementTask()

# /api/servers
async def get_servers_list() -> ServersListResponse:
    active_servers = await server_manager_task.get_online_servers()
    servers = {}
    player = 0

    for server in active_servers:
        player += active_servers[server].online
        servers[server] = ServerInfo(
            name=active_servers[server].display_name,
            online=active_servers[server].online,
            maxPlayers=active_servers[server].max_players,
        )
    return ServersListResponse(
        online_servers=len(active_servers), online_players=player, servers=servers
    )


async def create_new_server(
    db_session: AsyncSession = Depends(database_session_depends),
    form_data: ServerCreateFormRequest = Form(),
    access_payload: JwtAccessPayload = Depends(jwt_validator_depends),
) -> UUID:
    server, server_info = await create_server_by_form(
        session=db_session, 
        owner_user_id=int(access_payload.sub), 
        form_data=form_data
        )
    return server.uuid

# /api/servers/{server_uuid}
async def get_server_info(server_info: ServerModel = Depends(GetServerDepends())):
    return ServerModel.model_dump(server_info, mode="json")

async def update_server_settings(server_info: ServerModel = Depends(GetServerDepends())):
    raise NotImplementedError


async def delete_server(server_info: ServerModel = Depends(GetServerDepends())):
    raise NotImplementedError


async def server_hearbeat(
    server_uuid: UUID,
    server_info: ServerInfo,
    server_data: ServerModel = Depends(GetServerDepends()),
) -> None:
    if not server_data.info.host:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if await server_manager_task.get_server(server_uuid=server_uuid):
        await server_manager_task.update_server(
            server_uuid=server_uuid, online=server_info.online
        )
    else:
        try:
            async with httpx.AsyncClient() as client:
                response_manifest = await client.get(
                    f"http://{server_data.info.host}:{server_data.info.main_port + 1}/manifest.json"
                )
                response_manifest.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise HTTPException(
                status_code=error.response.status_code, detail=str(error)
            )
        except httpx.RequestError:
            raise HTTPException(status_code=400, detail="Server data is not correct")

        manifest = ServerModsManifest.model_validate(response_manifest.json())
        storage = ServerStorage(
            display_name=server_info.name,
            host=server_data.info.host,
            port=server_data.info.main_port,
            online=server_info.online,
            max_players=server_info.max_players,
            gamemode=server_data.info.gamemode_type,
            manifest=manifest,
        )
        await server_manager_task.add_server(server_uuid=server_uuid, storage=storage)
        # Заголовок `Location` передается адрес созданного ресурса. Добавить возвращение UUID в заголовок


async def get_server_online(server_uuid: UUID) -> int:
    if server := await server_manager_task.get_server(server_uuid):
        return server.online
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def get_connect_info(server_uuid: UUID, 
) -> ServerConnectResponse:
    if server := await server_manager_task.get_server(server_uuid):
        return ServerConnectResponse(
            key=server_uuid, host=server.host, port=server.port
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def get_manifest(
    server_uuid: UUID,
):
    if server := await server_manager_task.get_server(server_uuid):
        return server.manifest
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

async def сreating_server_session(
    server_uuid: UUID,
    real_ip: IPv4Address = Depends(get_client_ip_depends),
    db_session: AsyncSession = Depends(database_session_depends),
    redis_client: redis.Redis = Depends(redis_client_depends),
    authorization: str = Header(),
):
    user_id = await redis_client.get(name=f"session_token:{authorization}")
    if user_id:
        session = secrets.token_urlsafe()
        await create_game_session(
            session=db_session, 
            user_id=int(user_id), 
            server_uuid=server_uuid, 
            session_token=session, 
            user_ip=real_ip
        )
    return {"session": session}
        


async def get_user_sessions(
    sessions: str,
    server_data: Optional[ServerModel] = Depends(GetServerDepends()),
    db_session: AsyncSession = Depends(database_session_depends),
):
    if not server_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    game_session = await read_game_session_by_token(session=db_session, session_token=sessions)
    if not game_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"user":{"id":game_session.user_id}}
