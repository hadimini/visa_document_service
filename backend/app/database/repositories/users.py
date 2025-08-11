from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.database.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

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
