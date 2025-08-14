import bcrypt
import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import ValidationError

from app.config import (
    SECRET_KEY,
    JWT_ALGORITHM,
)
from app.models.users import User
from app.schemas.token import JWTMeta, JWTCreds, JWTPayload
from app.schemas.user import UserPasswordUpdate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def generate_salt(self) -> str:
        return bcrypt.gensalt().decode()

    def hash_password(self, *, password: str, salt: str) -> str:
        return pwd_context.hash(password + salt)

    def create_salt_and_hashed_password(self, *, plaintext_password: str) -> UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt)
        return UserPasswordUpdate(password=hashed_password, salt=salt)

    def verify_password(self, *, password: str, salt: str, hashed_password: str) -> bool:
        return pwd_context.verify(password + salt, hashed_password)

    def create_access_token(
            self,
            *,
            user: User,
            secret_key: str = str(SECRET_KEY),
    ) -> str:
        jwt_meta = JWTMeta()
        jwt_creds = JWTCreds(email=user.email, first_name=user.first_name, last_name=user.last_name)
        token_payload = JWTPayload(**jwt_meta.model_dump(), **jwt_creds.model_dump())
        access_token = jwt.encode(token_payload.model_dump(), secret_key, algorithm=JWT_ALGORITHM)
        return access_token

    def get_email_from_token(self, *, token: str, secret_key: str) -> User | None:
        try:
            decoded_token = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
            payload = JWTPayload(**decoded_token)
        except (jwt.PyJWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.email
