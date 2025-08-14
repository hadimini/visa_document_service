from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.v1 import EmailStr

# from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_repository
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.token import AccessToken, TokenPair
from app.schemas.user import UserPublic, UserCreate
from app.services import auth_service, jwt_service


router = APIRouter()


@router.get("/", response_model=list[UserPublic], name="users:user-list")
async def list(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    users = await users_repo.get_all()
    return users

@router.post("/", response_model=UserPublic, name="users:users-create", status_code=status.HTTP_201_CREATED)
async def create(
        new_user: UserCreate,
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    created_user = await user_repo.create(new_user=new_user)
    return created_user


@router.get("/get/{user_id}", response_model=UserPublic, name="users:users-get")
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
    return token_pair.access.token
