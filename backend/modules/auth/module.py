from fastapi import APIRouter, FastAPI, status

from shared.interfaces import BaseModule
from shared.enum import Environment

from .routing import (
    login,
    signup,
    logout,
    reset_password_request,
    reset_password,
)

class AuthModule(BaseModule):
    name = "Auth Module"
    description = "Module for registering and authorizing users using login credentials"
    version = "0.1.0"
    dependencies = []
    tags = "Auth"
    prefix = "/auth"

    def setup_module(self, environment: Environment, app: FastAPI):
        if self.router:
            # /api/auth
            auth_router = APIRouter(prefix="")
            auth_router.post("/login", status_code=status.HTTP_200_OK)(login)
            auth_router.post("/signup", status_code=status.HTTP_201_CREATED)(signup)
            auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)(logout)
            auth_router.post("/reset_password", status_code=status.HTTP_202_ACCEPTED)(reset_password_request)
            auth_router.get("/reset_password/{reset_token}", status_code=status.HTTP_200_OK)(reset_password)
            # Добавить возможность смены пароля
            
            # Include
            self.router.include_router(auth_router)


