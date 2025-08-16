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
    TokenPairSchema,
    JWTMetaSchema,
    JWTCredsSchema,
    JWTPayloadSchema
)


class JWTService:

    def create_access_token(self, *, payload: JWTPayloadSchema, minutes: int | None = None) -> JWTSchema:
        expire = datetime.now() + timedelta(
            minutes=minutes or JWT_ACCESS_TOKEN_EXPIRES_MINUTES
        )
        expire = int(expire.timestamp())
        payload: JWTPayloadSchema = payload.copy(update={"exp": expire})
        token = JWTSchema(
            token=jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )
        return token

    def _create_refresh_token(self, *, payload: JWTPayloadSchema) -> JWTSchema:
        expire = datetime.now() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
        expire = int(expire.timestamp())
        payload: JWTPayloadSchema = payload.copy(update={"exp": expire})
        token = JWTSchema(
            token=jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )

        return token

    def create_token_pair(self, *, user: User) -> TokenPairSchema | None:
        if not user:
            return None

        token_meta: JWTMetaSchema = JWTMetaSchema(
            jti=str(uuid.uuid4()),
            iat=int(datetime.now().timestamp()),
            sub=None
        )
        token_creds: JWTCredsSchema = JWTCredsSchema(sub=str(user.id))
        payload: JWTPayloadSchema = JWTPayloadSchema(
            **token_meta.model_dump(),
            **token_creds.model_dump()
        )
        pair = TokenPairSchema(
            access=self.create_access_token(payload=payload),
            refresh=self._create_refresh_token(payload=payload)
        )
        return pair

    def decode_token(self, *, token: str) -> JWTPayloadSchema:
        payload: dict = jwt.decode(
            jwt=token,
            key=str(SECRET_KEY),
            algorithms=[str(JWT_ALGORITHM)],
        )

        return JWTPayloadSchema(**payload)
