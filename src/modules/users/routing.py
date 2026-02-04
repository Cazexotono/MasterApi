
from fastapi import Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from shared.depends import database_session_depends
from shared.crud import read_user_info_by_id, update_user_info_by_id

from .schema.form import FormUpdatePublicInfo

# TODO
# Добавить режимы приватности
async def get_user_info(
    user_id: int, 
    db_session: AsyncSession = Depends(database_session_depends),
    ):
    return await read_user_info_by_id(session=db_session, user_id=user_id)


async def update_user_public_info(
    user_id: int,
    db_session: AsyncSession = Depends(database_session_depends),
    form_data: FormUpdatePublicInfo = Form(),
    ):
    update_form = await update_user_info_by_id(session=db_session, user_id=user_id, data=form_data.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True))
    return update_form

async def delete_user(
    user_id: int,
    ):
    raise NotImplementedError


async def get_user_servers(
    user_id: int,
    ):
    raise NotImplementedError


async def get_user_sessions(
    user_id: int,
    ):
    raise NotImplementedError