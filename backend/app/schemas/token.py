from datetime import datetime, timedelta

from pydantic import EmailStr

from app.config import JWT_AUDIENCE, JWT_EXPIRE_MINUTES
from app.schemas.core import CoreModel


class JWTMeta(CoreModel):
    iss: str = 'visasupper.eu'  # the issuer of the token
    aud: str = JWT_AUDIENCE  # who is this token intended for?
    iat: float = datetime.timestamp(datetime.now())  # issued at
    exp: float = datetime.timestamp(datetime.now() + timedelta(minutes=JWT_EXPIRE_MINUTES))  # expires at


class JWTCreds(CoreModel):
    """How we will identify users"""
    email: EmailStr


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """
    pass


class AccessToken(CoreModel):
    access_token: str
    token_type: str
