from datetime import datetime
from uuid import UUID

from app.schemas.core import CoreSchema


class JWTMetaSchema(CoreSchema):
    jti: str
    iat: int
    exp: int | None = None


class JWTCredsSchema(CoreSchema):
    sub: str  # SUBJECT MUST BE A STRING
    type: str | None = None
    role: str | None = None


class JWTPayloadSchema(JWTMetaSchema, JWTCredsSchema):
    pass


class TokenPairSchema(CoreSchema):
    access: str
    refresh: str


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
