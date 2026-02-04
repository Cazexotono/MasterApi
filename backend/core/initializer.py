import logging

from shared.enum import Environment
from shared.logs import console_handler, file_handler

from .settings.settings_provider import ProjectSchema, ApiSettings, SecretSettings
from .database.alchemy_manager import SqlAlchemyManager
from .cache.redis_manager import RedisManager

__all__ = (    
    "project",
    "settings",
    "secret",
    "database_manager",
    "redis_manager",
    "SecretSettings",
)

# Logs
logger_console = logging.getLogger("console")
logger_console.addHandler(console_handler)
logger_console.propagate = False 

logger_app = logging.getLogger("app")
logger_app.addHandler(console_handler)
logger_app.addHandler(file_handler)
logger_app.propagate = False

# Settings
project = ProjectSchema()
settings = ApiSettings()
secret = SecretSettings()

match settings.environment:
    case Environment.dev:
        logger_console.setLevel(logging.DEBUG)
        logger_app.setLevel(logging.DEBUG)
    case Environment.staging:
        logger_console.setLevel(logging.INFO)
        logger_app.setLevel(logging.WARNING)
    case Environment.production:
        logger_console.setLevel(logging.INFO)
        logger_app.setLevel(logging.ERROR)



# Providers
if not settings.database.db_url or not settings.redis.cache_url:
    raise ValueError("PostgresDsn or RedisDsn not found")
database_manager = SqlAlchemyManager(settings.database.db_url)
redis_manager = RedisManager(settings.redis.cache_url)