from pydantic import EmailStr

from app.schemas.core import CoreModel, IDModelMixin, DateTimeModelMixin


class UserBase(CoreModel):
    email: EmailStr
    email_verified: bool = False
    is_active: bool = True


class UserInDB(UserBase):
    password: str
    salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    pass
