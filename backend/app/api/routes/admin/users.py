from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_repository
from app.database.repositories.users import UsersRepository
from app.exceptions import NotFoundException
from app.schemas.pagination import PageParamsSchema
from app.schemas.user import UserResponseSchema, UserFilterSchema, UserListResponseSchema

router = APIRouter()


@router.get("", response_model=UserListResponseSchema, name="admin:user-list")
async def user_list(
        query_filters: UserFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    result: dict[str, Any] = await users_repo.get_paginated_list(query_filters=query_filters, page_params=page_params)
    return result


@router.get("/{user_id}", response_model=UserResponseSchema, name="admin:user-detail")
async def user_detail(
        user_id: int,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user = await users_repo.get_by_id(user_id=user_id)

    if not user:
        raise NotFoundException(detail="User not found")
    return user
