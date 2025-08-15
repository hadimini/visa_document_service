import uuid
from datetime import datetime, timedelta

import jwt

from app.config import (
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES,
    SECRET_KEY
)
from app.models.users import User
from app.schemas.token import (
    JWTSchema,
    TokenPair,
    JWTMeta,
    JWTCreds,
    JWTPayload
)


class JWTService:

    def create_access_token(self, *, payload: JWTPayload, minutes: int | None = None) -> JWTSchema:
        expire = datetime.now() + timedelta(
            minutes=minutes or JWT_ACCESS_TOKEN_EXPIRES_MINUTES
        )
        expire = int(expire.timestamp())
        payload: JWTPayload = payload.copy(update={"exp": expire})
        token = JWTSchema(
            token=jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )
        return token

    def _create_refresh_token(self, *, payload: JWTPayload) -> JWTSchema:
        expire = datetime.now() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
        expire = int(expire.timestamp())
        payload: JWTPayload = payload.copy(update={"exp": expire})
        token = JWTSchema(
            token=jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )

        return token

    def create_token_pair(self, *, user: User) -> TokenPair | None:
        if not user:
            return None

        token_meta: JWTMeta = JWTMeta(
            jti=str(uuid.uuid4()),
            iat=int(datetime.now().timestamp()),
            sub=None
        )
        token_creds: JWTCreds = JWTCreds(sub=str(user.id))
        payload: JWTPayload = JWTPayload(
            **token_meta.model_dump(),
            **token_creds.model_dump()
        )
        pair = TokenPair(
            access=self.create_access_token(payload=payload),
            refresh=self._create_refresh_token(payload=payload)
        )
        return pair

    def decode_token(self, *, token: str) -> JWTPayload:
        payload: dict = jwt.decode(
            jwt=token,
            key=str(SECRET_KEY),
            algorithms=[str(JWT_ALGORITHM)],
        )

        return JWTPayload(**payload)
