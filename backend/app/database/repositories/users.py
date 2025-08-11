from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.database.repositories.base import BaseRepository
from app.schemas.user import UserInDB


class UsersRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_all(self) -> list[UserInDB]:
        statement = select(User).order_by(User.id)
        result = await self.db.execute(statement)
        users = result.scalars().all()
        return users

    async def get_by_id(self, *, id: int) -> UserInDB:
        statement = select(User).where(User.id == id)
        result = await self.db.execute(statement)
        user = result.scalars().first()

        print('\n\n\nUser: ', user)
        if user:
            return user
