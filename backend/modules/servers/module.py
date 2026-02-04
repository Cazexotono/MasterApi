from fastapi import APIRouter, FastAPI, status, Depends

from shared.interfaces import BaseModule
from shared.enum import Environment
from .utils import GetServerDepends
from .routing import (
    get_servers_list,
    create_new_server,
    get_server_info,
    server_hearbeat,
    update_server_settings,
    delete_server,
    get_server_online,
    get_connect_info,
    get_manifest,
    get_user_sessions,
    сreating_server_session,
    server_manager_task
)


class ServerModule(BaseModule):
    name = "Server Module"
    description = "Module for creating, managing, and monitoring online servers"
    version = "0.1.0"
    dependencies = []
    tags = "Servers"
    prefix = "/servers"

    def setup_module(self, environment: Environment, app: FastAPI):
        if self.router:
            # /api/servers
            self.router.post("", status_code=status.HTTP_201_CREATED)(create_new_server)
            self.router.get("", status_code=status.HTTP_200_OK)(get_servers_list)

            # /api/servers/{server_uuid}
            servers_router = APIRouter(prefix="/{server_uuid}", dependencies=[Depends(GetServerDepends(cache_ttl=1800))])
            servers_router.get("", status_code=status.HTTP_200_OK)(get_server_info)
            servers_router.post("", status_code=status.HTTP_204_NO_CONTENT)(server_hearbeat)
            servers_router.patch("", status_code=status.HTTP_200_OK)(update_server_settings)
            servers_router.delete("", status_code=status.HTTP_204_NO_CONTENT)(delete_server)
            servers_router.get("/online", status_code=status.HTTP_200_OK)(get_server_online)
            servers_router.get("/serverinfo", status_code=status.HTTP_200_OK)(get_connect_info)
            servers_router.get("/manifest.json", status_code=status.HTTP_200_OK)(get_manifest)
            servers_router.post("/sessions", status_code=status.HTTP_200_OK)(сreating_server_session)
            servers_router.get("/sessions/{sessions}", status_code=status.HTTP_200_OK)(get_user_sessions)

            # Include router
            self.router.include_router(servers_router)

            # Include tasks
            self.tasks.append(server_manager_task)


