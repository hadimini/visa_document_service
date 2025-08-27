from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.visa_types import VisaType
from app.schemas.visa_type import VisaTypeCreateSchema, VisaTypeUpdateSchema


class VisaTypesRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.db = db

    async def get_list(self):
        statement = select(VisaType).order_by(VisaType.id)
        result = await self.db.execute(statement)
        visa_types = result.scalars().all()
        return visa_types

    async def get_by_id(self, *, visa_type_id: int) -> VisaType:
        statement = select(VisaType).where(VisaType.id == visa_type_id)
        result = await self.db.execute(statement)
        visa_type = result.scalars().one_or_none()
        return visa_type

    async def create(self, *, data: VisaTypeCreateSchema) -> VisaType:
        visa_type = VisaType(**data.model_dump())
        self.db.add(visa_type)
        await self.db.commit()
        return visa_type

    async def update(self, *, visa_type_id: int, data: VisaTypeUpdateSchema) -> VisaType:
        visa_type = await self.get_by_id(visa_type_id=visa_type_id)

        if visa_type:
            for attr, value in data.model_dump().items():
                setattr(visa_type, attr, value)
            return visa_type
