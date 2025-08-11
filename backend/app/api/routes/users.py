from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.db import get_repository
from app.database.repositories.users import UsersRepository
from app.schemas.user import UserPublic


router = APIRouter()


@router.get("/", response_model=list[UserPublic], name="users:user-list")
async def list(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    users = await users_repo.get_all()
    return users

@router.get("/{id}", response_model=UserPublic, name="users:users-get")
async def get(
        id: int,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user = await user_repo.get_by_id(id=id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
