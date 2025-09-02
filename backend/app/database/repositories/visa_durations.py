from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models import VisaDuration


class VisaDurationsRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def create(self, term: str, entry: str) -> VisaDuration:
        visa_duration = VisaDuration(
            term=term,
            entry=entry,
        )
        self.db.add(visa_duration)
        await self.db.commit()
        return visa_duration
