from fastapi import APIRouter, Depends

from app.api.dependencies.auth import role_required
from app.api.dependencies.db import get_repository
from app.api.helpers import paginate
from app.database.repositories.users import UsersRepository
from app.exceptions import NotFoundException
from app.models.users import User
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from app.schemas.user import UserPublicSchema, UserFilterSchema

router = APIRouter()


@router.get("/", response_model=PagedResponseSchema, name="admin:user-list")
async def user_list(
        filters: UserFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    results: list[User] = await users_repo.get_all(filters=filters, page_params=page_params)
    return paginate(
        page_params,
        results,
        UserPublicSchema
    )


@router.get("/{user_id}", response_model=UserPublicSchema, name="admin:user-detail")
async def user_detail(
        user_id: int,
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user = await users_repo.get_by_id(user_id=user_id)

    if not user:
        raise NotFoundException(detail="User not found")
    return user
