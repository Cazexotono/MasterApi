from shared.interfaces import BaseModule

from fastapi import APIRouter, FastAPI

from shared.enum import Environment
from .routing import (
    get_user_info,
    update_user_public_info,
    delete_user,
    get_user_servers,
    get_user_sessions,
)


class UsersModule(BaseModule):
    name = "Users Module"
    description = "Module for user management"
    version = "0.1.0"
    dependencies = []
    tags = "Users"
    prefix = "/users"

    def setup_module(self, environment: Environment, app: FastAPI):
        if self.router:
            # /api/users/{user_id}
            user_router = APIRouter(prefix="/{user_id}")
            user_router.get("")(get_user_info)
            user_router.patch("")(update_user_public_info)
            user_router.delete("")(delete_user)
            user_router.get("/servers")(get_user_servers)
            user_router.get("/sessions")(get_user_sessions)

            self.router.include_router(user_router)
