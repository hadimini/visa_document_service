from collections.abc import Sequence

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.audit import LogEntry
from app.schemas.audit import LogEntryCreateSchema


class AuditRepository(BaseRepository):
    def __int__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, new_entry: LogEntryCreateSchema) -> LogEntry:
        entry: LogEntry = LogEntry(**new_entry.model_dump())
        self.db.add(entry)
        await self.db.commit()
        return entry

    async def get_for_user(self, *, user_id: int) -> Sequence[LogEntry]:
        statement = select(LogEntry).where(LogEntry.user_id == user_id).order_by(desc(LogEntry.id))
        results = await self.db.execute(statement)
        return results.scalars().all()
