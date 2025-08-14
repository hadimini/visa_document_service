from datetime import datetime

from app.schemas.core import CoreModel


class JWTPayload(CoreModel):
    sub: int
    jti: str
    iat: int
    exp: int


class JWTSchema(CoreModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(CoreModel):
    access: JWTSchema
    refresh: JWTSchema


class TokenVerify(CoreModel):
    token: str


class RefreshToken(CoreModel):
    refresh: str


class AccessToken(CoreModel):
    access_token: str
    token_type: str
