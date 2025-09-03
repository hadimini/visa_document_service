from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database.repositories.base import BaseRepository
from app.exceptions import ObjectExistsException
from app.models import CountryVisa, VisaDuration, country_visa_duration
from app.schemas.country_visa import CountryVisaCreateSchema, CountryVisaAdminUpdateSchema


class CountryVisasRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.db = db

    async def _get_visa_durations_by_ids(self, duration_ids: list[int]) -> list[VisaDuration]:
        """
        Get visa durations by ids.
        :param duration_ids:
        :return:
        """
        if not duration_ids:
            return []

        statement = select(VisaDuration).where(VisaDuration.id.in_(duration_ids))
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def _update_visa_durations(self, *, country_visa: CountryVisa, new_duration_ids: list[int] = None) -> None:
        await country_visa.awaitable_attrs.visa_durations
        country_visa.visa_durations.clear()

        if new_duration_ids:
            visa_durations = await self._get_visa_durations_by_ids(new_duration_ids)
            country_visa.visa_durations.extend(visa_durations)


    async def get_list(self, *, country_id: int = None) -> Sequence[CountryVisa]:
        options = [
            joinedload(CountryVisa.visa_type),
            selectinload(CountryVisa.visa_durations)
        ]

        statement = select(CountryVisa).options(
            *options
        ).order_by(CountryVisa.id)

        if country_id:
            statement = statement.where(CountryVisa.country_id == country_id)

        result = await self.db.scalars(statement)
        result = result.all()
        return result


    async def get_by_id(self, *, country_visa_id: int, populate_duration_data: bool = False) -> CountryVisa | None:
        """Get CountryVisa by ID with optional duration data population."""
        options = [joinedload(CountryVisa.visa_type)]

        if populate_duration_data:
            options.append(selectinload(CountryVisa.visa_durations))

        statement = select(CountryVisa).options(*options).where(CountryVisa.id == country_visa_id)

        result = await self.db.execute(statement)
        country_visa = result.scalars().one_or_none()

        if not country_visa or not populate_duration_data:
            return country_visa

        available_visa_durations = await self.db.scalars(
            select(VisaDuration)
            .where(
                ~VisaDuration.id.in_(
                    select(country_visa_duration.c.visa_duration_id)
                    .where(country_visa_duration.c.country_visa_id == country_visa_id)
                )
            )
            .order_by(VisaDuration.id)
        )

        country_visa.duration_data = {
            "attached": country_visa.visa_durations or None,
            "available": available_visa_durations.all() or None
        }

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

    async def update(self, *, country_visa_id: int, data: CountryVisaAdminUpdateSchema) -> CountryVisa | None:
        country_visa = await self.get_by_id(country_visa_id=country_visa_id)

        if not country_visa:
            return None
        update_data = data.model_dump(exclude_unset=True, exclude={"visa_duration_ids"})

        for attr, value in update_data.items():
            setattr(country_visa, attr, value)

        if data.visa_duration_ids is not None:
            await self._update_visa_durations(
                country_visa=country_visa,
                new_duration_ids=data.visa_duration_ids
            )

        await self.db.commit()
        await self.db.refresh(country_visa, ["visa_durations"])

        country_visa = await self.get_by_id(country_visa_id=country_visa_id, populate_duration_data=True)
        return country_visa
