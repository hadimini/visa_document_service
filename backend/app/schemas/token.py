from datetime import datetime

from app.schemas.core import CoreModel


class JWTMeta(CoreModel):
    jti: str
    iat: int
    exp: int | None = None


class JWTCreds(CoreModel):
    sub: str


class JWTPayload(JWTMeta, JWTCreds):
    pass


class JWTSchema(CoreModel):
    token: str
    payload: JWTPayload
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
