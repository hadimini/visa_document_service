from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.db import get_repository
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.token import JWTPayload
from app.services import jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_user_from_token(
        *,
        token: str = Depends(oauth2_scheme),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> User | None:

    try:
        payload: JWTPayload = jwt_service.decode_token(token=token)
        user = await user_repo.get_by_id(user_id=int(payload.sub))
    except Exception as e:
        raise e
    else:
        return user


async def get_current_active_user(current_user: User = Depends(get_user_from_token)) -> User | None:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user
