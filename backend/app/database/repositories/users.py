from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.users import User
from app.schemas.user import UserCreate, UserCreateInDB
from app.services.auth import AuthService


class UsersRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.auth_service = AuthService()

    async def create(self, *, new_user: UserCreate) -> User:
        user_password_update = self.auth_service.create_salt_and_hashed_password(
            plaintext_password=new_user.password
        )
        new_user = UserCreateInDB(**new_user.model_dump(exclude={"password"}), **user_password_update.model_dump())
        new_user = User(**new_user.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        return new_user

    async def get_all(self) -> list[User]:
        statement = select(User).order_by(User.id)
        result = await self.db.execute(statement)
        users = result.scalars().all()
        return list(users)

    async def get_by_id(self, *, id: int) -> User | None:
        statement = select(User).where(User.id == id)
        result = await self.db.execute(statement)
        user = result.one_or_none()
        return user[0] if user else None

    async def get_by_email(self, *, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        user = result.one_or_none()
        return user[0]
