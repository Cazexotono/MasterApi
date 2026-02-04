from fastapi import APIRouter, FastAPI

from shared.interfaces import BaseModule
from shared.enum import Environment

class UsersModule(BaseModule):
    name = "Core Module"
    description = "A module for obtaining information about the API and its status and systems"
    version = "0.1.0"
    dependencies = []
    tags = "Core"
    prefix = ""

    def setup_module(self, environment: Environment, app: FastAPI):
        if self.router:
            # /api/
            self.router.get("/info")
            self.router.get("/health")
            self.router.get("/ready")
            self.router.get("/metrics")