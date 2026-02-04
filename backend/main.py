import uvicorn
from core import settings, database_manager, redis_manager, FastApiBuilder, ModuleLoader

from shared.depends import jwt_validator_depends

managers = [database_manager, redis_manager]
loader = ModuleLoader(modules_package_name="modules")

app = FastApiBuilder(
    environment=settings.environment, 
    modules=loader.get_moduls(),
    managers=managers,
    global_depends=[jwt_validator_depends]
    )

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.host,
        port=settings.port,
        reload= settings.environment == "dev",
    )