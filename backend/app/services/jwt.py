import uuid
from datetime import datetime, timedelta

import jwt

from app.config import (
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES,
    JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_MINUTES,
    SECRET_KEY
)
from app.models.users import User
from app.schemas.token import (
    TokenPairSchema,
    JWTMetaSchema,
    JWTCredsSchema,
    JWTPayloadSchema
)


class JWTService:
    TYPE_AUTH_TOKEN = "auth"
    TYPE_EMAIL_CONFIRMATION_TOKEN = "email_confirmation"

    def create_access_token(self, *, payload: JWTPayloadSchema, minutes: int | None = None) -> str:
        expire = datetime.now() + timedelta(
            minutes=minutes or JWT_ACCESS_TOKEN_EXPIRES_MINUTES
        )
        expire = int(expire.timestamp())
        payload: JWTPayloadSchema = payload.model_copy(update={"exp": expire})
        return jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM))

    def create_refresh_token(self, *, payload: JWTPayloadSchema) -> str:
        expire = datetime.now() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
        expire = int(expire.timestamp())
        payload: JWTPayloadSchema = payload.model_copy(update={"exp": expire})
        return jwt.encode(payload=payload.model_dump(), key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM))

    def create_token_pair(self, *, user: User) -> TokenPairSchema | None:
        if not user:
            return None

        token_meta: JWTMetaSchema = JWTMetaSchema(
            jti=str(uuid.uuid4()),
            iat=int(datetime.now().timestamp())
        )
        token_creds: JWTCredsSchema = JWTCredsSchema(sub=str(user.id), type=self.TYPE_AUTH_TOKEN, role=user.role)
        payload: JWTPayloadSchema = JWTPayloadSchema(
            **token_meta.model_dump(),
            **token_creds.model_dump()
        )
        pair = TokenPairSchema(
            access=self.create_access_token(payload=payload),
            refresh=self.create_refresh_token(payload=payload)
        )
        return pair

    def create_email_confirmation_token(self, *, user: User) -> str:
        token_meta = JWTMetaSchema(
            jti=str(uuid.uuid4()),
            iat=int(datetime.now().timestamp())
        )
        token_creds = JWTCredsSchema(sub=str(user.id), type=self.TYPE_EMAIL_CONFIRMATION_TOKEN)
        payload = JWTPayloadSchema(
            **token_meta.model_dump(),
            **token_creds.model_dump()
        )
        token = self.create_access_token(payload=payload, minutes=JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_MINUTES)
        return token

    def verify_email_confirmation_token(self, *, token: str) -> JWTPayloadSchema | None:
        try:
            payload = self.decode_token(token=token)
            if payload.type != self.TYPE_EMAIL_CONFIRMATION_TOKEN:
                return None
            return payload
        except jwt.exceptions.PyJWTError:
            return None

    def decode_token(self, *, token: str) -> JWTPayloadSchema:
        payload: dict = jwt.decode(
            jwt=token,
            key=str(SECRET_KEY),
            algorithms=[str(JWT_ALGORITHM)],
        )
        return JWTPayloadSchema(**payload)
