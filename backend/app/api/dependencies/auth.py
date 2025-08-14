from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.db import get_repository
from app.config import SECRET_KEY, API_PREFIX
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.services import auth_service

oauth_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/users/login")


async def get_user_from_token(
        *,
        token: str = Depends(oauth_scheme),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> User | None:
    email = auth_service.get_email_from_token(token=token, secret_key=str(SECRET_KEY))
    user = await user_repo.get_by_email(email=email)

    return user


async def get_current_user(
        current_user: User = Depends(get_user_from_token)
) -> User | None:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an active user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
