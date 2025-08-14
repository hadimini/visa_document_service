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
    TokenPair
)


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"

# jwt.encode({"sub": "test"}, "T1KDz6lY8_joerpiTFc2QDnFOG4G7_Z78QJj5jkjXSI", algorithm="HS256")
# decoded = jwt.decode(new_token, "T1KDz6lY8_joerpiTFc2QDnFOG4G7_Z78QJj5jkjXSI", algorithms=["HS256"])
class JWTService:

    def create_access_token(self, *, payload: dict, minutes: int | None = None) -> JWTSchema:
        expire = datetime.now() + timedelta(
            minutes=minutes or JWT_ACCESS_TOKEN_EXPIRES_MINUTES
        )
        payload[EXP] = expire
        token = JWTSchema(
            token=jwt.encode(payload=payload, key=str(SECRET_KEY), algorithm=str(JWT_ALGORITHM)),
            payload=payload,
            expire=expire,
        )
        return token

    def _create_refresh_token(self, *, payload: dict) -> JWTSchema:
        expire = datetime.now() + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
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
            IAT: str(datetime.now())
        }

        pair = TokenPair(
            access=self.create_access_token(payload=payload),
            refresh=self._create_refresh_token(payload=payload)
        )
        return pair

    def decode_access_token(self, *, token: str):
        payload = jwt.decode(
            token,
            str(SECRET_KEY),
            algorithms=[str(JWT_ALGORITHM)],
        )

        return payload
