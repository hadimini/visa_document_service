from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.db import get_repository
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.token import TokenPair, TokenVerify
from app.schemas.user import UserPublic, UserCreate
from app.services import jwt_service

router = APIRouter()


@router.get("/", response_model=list[UserPublic], name="users:user-list")
async def list(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    users = await users_repo.get_all()
    return users

@router.post("/", response_model=UserPublic, name="users:user-create", status_code=status.HTTP_201_CREATED)
async def create(
        new_user: UserCreate,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    created_user = await user_repo.create(new_user=new_user)
    return created_user


@router.get("/get/{user_id}", response_model=UserPublic, name="users:user-detail")
async def get(
        user_id: int,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user = await user_repo.get_by_id(user_id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/login", name="users:user-login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    user: User = await user_repo.authenticate(email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token_pair: TokenPair = jwt_service.create_token_pair(user=user)
    return {
        "token": token_pair.access.token
    }


@router.get("/me", response_model=UserPublic, name="users:user-me")
async def profile(
        current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.post("/verify_token", name="users:user-token-verify")
async def verify_token(
        token_data: TokenVerify,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    payload = jwt_service.decode_token(token=token_data.token)
    user = await user_repo.get_by_id(user_id=int(payload.sub))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "msg": "success"
    }
