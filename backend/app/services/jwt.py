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
    JWTPayload
)


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


class JWTService:

    def create_access_token(self, *, payload: dict, minutes: int | None = None) -> JWTSchema:
        expire = datetime.now() + timedelta(
            minutes=minutes or JWT_ACCESS_TOKEN_EXPIRES_MINUTES
        )
        expire = int(expire.timestamp())
        payload[EXP] = expire
        token = JWTSchema(
            token=jwt.encode(payload=payload, key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )
        return token

    def _create_refresh_token(self, *, payload: dict) -> JWTSchema:
        expire = datetime.now() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
        expire = int(expire.timestamp())
        payload[EXP] = expire
        token = JWTSchema(
            token=jwt.encode(payload=payload, key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )

        return token

    def create_token_pair(self, *, user: User) -> TokenPair:
        payload = {
            SUB: str(user.id),
            JTI: str(uuid.uuid4()),
            IAT: int(datetime.now().timestamp())
        }

        pair = TokenPair(
            access=self.create_access_token(payload=payload),
            refresh=self._create_refresh_token(payload=payload)
        )
        return pair

    def decode_access_token(self, *, token: str) -> JWTPayload:
        payload = jwt.decode(
            jwt=token,
            key=str(SECRET_KEY),
            algorithms=[str(JWT_ALGORITHM)],
        )

        return JWTPayload(**payload)
