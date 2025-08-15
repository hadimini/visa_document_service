from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.api.dependencies.db import get_repository
from app.database.repositories.tokens import TokensRepository
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.token import JWTPayloadScheme
from app.services import jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_user_from_token(
        *,
        token: str = Depends(oauth2_scheme),
        tokens_repo: TokensRepository = Depends(get_repository(TokensRepository)),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> User | None:
    try:
        payload: JWTPayloadScheme = jwt_service.decode_token(token=token)
        # Check if token is blacklisted
        if await tokens_repo.get_by_id(token_id=payload.jti):
            raise InvalidTokenError()

        user = await users_repo.get_by_id(user_id=int(payload.sub))
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is blacklisted.",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
