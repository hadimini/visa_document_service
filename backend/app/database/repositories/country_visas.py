from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository
from app.exceptions import ObjectExistsException
from app.models.country_visas import CountryVisa
from app.schemas.country_visa import CountryVisaCreateSchema, CountryVisaUpdateSchema


class CountryVisasRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.db = db

    async def get_list(self) -> Sequence[CountryVisa]:
        statement = select(CountryVisa).order_by(CountryVisa.id)
        result = await self.db.scalars(statement)
        return result.all()

    async def get_by_id(self, *, country_visa_id: int) -> CountryVisa:
        statement = select(CountryVisa).where(CountryVisa.id == country_visa_id)
        result = await self.db.execute(statement)
        country_visa = result.scalars().one_or_none()
        return country_visa

    async def exists(self, country_id: int, visa_type_id: int) -> bool:
        statement = select(CountryVisa).where(
            CountryVisa.country_id == country_id,
            CountryVisa.visa_type_id == visa_type_id,
        )
        result = await self.db.execute(statement)
        return result.scalars().one_or_none() is not None

    async def create(self, *, data: CountryVisaCreateSchema) -> CountryVisa:
        if await self.exists(country_id=data.country_id, visa_type_id=data.visa_type_id):
            raise ObjectExistsException()
        country_visa = CountryVisa(**data.model_dump())

        self.db.add(country_visa)
        await self.db.commit()
        return country_visa

    async def update(self, *, country_visa_id: int, data: CountryVisaUpdateSchema) -> CountryVisa | None:
        country_visa = await self.get_by_id(country_visa_id=country_visa_id)

        if country_visa:
            for attr, value in data.model_dump().items():
                setattr(country_visa, attr, value)
            return country_visa
