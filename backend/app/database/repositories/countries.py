from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models import Country


class CountriesRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def get_all(self):
        statement = select(Country).order_by(Country.id)
        results = await self.db.execute(statement)
        return results.scalars().all()
