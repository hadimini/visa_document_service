from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.audit import LogEntry
from app.schemas.audit import EntryLogCreateSchema


class AuditRepository(BaseRepository):
    def __int__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, new_entry: EntryLogCreateSchema) -> LogEntry:
        entry = LogEntry(**new_entry.model_dump())
        self.db.add(entry)
        await self.db.commit()
        return entry
