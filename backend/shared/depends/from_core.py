from core import database_manager, redis_manager

__all__ = ("database_session_depends","redis_client_depends",)

database_session_depends = database_manager.get_session_depends
redis_client_depends = redis_manager.get_client_depends