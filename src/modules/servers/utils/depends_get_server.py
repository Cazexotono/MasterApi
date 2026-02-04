from typing import Optional

import redis
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.depends import redis_client_depends, database_session_depends
from .crud_server import read_server_by_UUID
from ..schema import ServerModel

class GetServerDepends:
    def __init__(
        self, 
        cache_ttl: int = 1800,
        ) -> None:
        self._ttl_expire = cache_ttl

    async def __call__(
        self,
        server_uuid: UUID,
        redis_client: redis.Redis = Depends(redis_client_depends),
        db_session: AsyncSession = Depends(database_session_depends),
    ) -> Optional[ServerModel]:
        cache_data = await redis_client.get(name=f"server:{str(server_uuid)}")
        if cache_data:
            server_data = ServerModel.model_validate_json(cache_data)
            await redis_client.expire(f"server:{str(server_uuid)}", self._ttl_expire)
        else:
            server_db = await read_server_by_UUID(db_session, server_uuid)
            if server_db:
                server_data = ServerModel.model_validate(server_db)
                await redis_client.set(name=f"server:{str(server_uuid)}", value=server_data.model_dump_json())
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return server_data


