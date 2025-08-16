from datetime import datetime
from uuid import UUID

from app.schemas.core import CoreSchema


class JWTMetaSchema(CoreSchema):
    jti: str
    iat: int
    exp: int | None = None


class JWTCredsSchema(CoreSchema):
    sub: str  # SUBJECT MUST BE A STRING

class JWTPayloadSchema(JWTMetaSchema, JWTCredsSchema):
    pass


class JWTSchema(CoreSchema):
    token: str
    payload: JWTPayloadSchema
    expire: datetime


class TokenPairSchema(CoreSchema):
    access: JWTSchema
    refresh: JWTSchema


class TokenVerifySchema(CoreSchema):
    token: str


class RefreshTokenSchema(CoreSchema):
    refresh: str


class AccessTokenSchema(CoreSchema):
    access_token: str
    token_type: str


class BlackListTokenSchema(CoreSchema):
    id: UUID
    expire: datetime
