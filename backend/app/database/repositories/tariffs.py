from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.models.tariffs import Tariff
from app.schemas.tariff import TariffCreateSchema


class TariffsRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, *, new_tariff: TariffCreateSchema) -> Tariff:
        # TODO: Check if default is true, and other is_default exists and update
        new_tariff = Tariff(**new_tariff.model_dump())
        self.db.add(new_tariff)
        await self.db.commit()
        return new_tariff
