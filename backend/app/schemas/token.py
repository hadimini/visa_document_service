from datetime import datetime
from uuid import UUID

from app.schemas.core import CoreScheme


class JWTMetaScheme(CoreScheme):
    jti: str
    iat: int
    exp: int | None = None


class JWTCredsScheme(CoreScheme):
    sub: str  # SUBJECT MUST BE A STRING

class JWTPayloadScheme(JWTMetaScheme, JWTCredsScheme):
    pass


class JWTSchema(CoreScheme):
    token: str
    payload: JWTPayloadScheme
    expire: datetime


class TokenPairScheme(CoreScheme):
    access: JWTSchema
    refresh: JWTSchema


class TokenVerifyScheme(CoreScheme):
    token: str


class RefreshTokenScheme(CoreScheme):
    refresh: str


class AccessTokenScheme(CoreScheme):
    access_token: str
    token_type: str


class BlackListTokenScheme(CoreScheme):
    id: UUID
    expire: datetime
