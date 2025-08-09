from fastapi import APIRouter, Depends
# from sqlalchemy import
from pydantic import TypeAdapter
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.api.dependencies.db import get_db, get_repository
from app.database.repositories.users import UsersRepository
from app.schemas.user import UserPublic


router = APIRouter()

# ta = TypeAdapter(list[UserBase])


@router.get("/", response_model=list[UserPublic], name="users:user-list")
async def get_users(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    users = await users_repo.get_all()
    return users
