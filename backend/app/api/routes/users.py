from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_db, get_repository
from app.database.repositories.users import UsersRepository
from app.schemas.user import UserPublic


router = APIRouter()


@router.get("/", response_model=list[UserPublic], name="users:user-list")
async def get_users(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    users = await users_repo.get_all()
    return users
