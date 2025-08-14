from datetime import datetime

from app.schemas.core import CoreModel


class JWTSchema(CoreModel):
    token: str
    payload: dict
    expire: datetime


class TokenPair(CoreModel):
    access: JWTSchema
    refresh: JWTSchema


class RefreshToken(CoreModel):
    refresh: str


class AccessToken(CoreModel):
    access_token: str
    token_type: str
