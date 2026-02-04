from shared.interfaces import BaseModule

from fastapi import APIRouter, FastAPI, status

from shared.enum import Environment
from .routing import create_status_tracking, get_state_status, update_status_tracking

class AuthStateModule(BaseModule):
    name = "Auth State Module"
    description = "Module for in-game user authorization"
    version = "0.1.0"
    dependencies = []
    tags = "Auth State"
    prefix = "/auth"

    def setup_module(self, environment: Environment, app: FastAPI):
        if self.router:
            # /auth/state
            state_router = APIRouter(prefix="/state")
            state_router.get("", status_code=status.HTTP_302_FOUND)(create_status_tracking)
            state_router.get("/status")(get_state_status)
            state_router.post("/status")(update_status_tracking)

            self.router.include_router(state_router)