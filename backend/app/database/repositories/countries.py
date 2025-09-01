from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.database.repositories.base import BaseRepository
from app.models import CountryVisa
from app.models.countries import Country
from app.schemas.country import CountryFilterSchema, CountryUpdateSchema
from app.schemas.pagination import PageParamsSchema


class CountriesRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db

    async def get_paginated_list(self, *, filters: CountryFilterSchema, page_params: PageParamsSchema):
        # First, get paginated country IDs
        count_stmt = select(Country.id)

        if filters.name:
            count_stmt = count_stmt.filter(Country.name.ilike(f"%{filters.name}%"))

        count_stmt = count_stmt.filter(Country.available_for_order == filters.available_for_order)
        count_stmt = count_stmt.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
        country_ids = (await self.db.scalars(count_stmt)).all()

        # Then fetch countries with relationships
        if country_ids:
            statement = select(Country).options(
                selectinload(Country.country_visas).selectinload(CountryVisa.visa_type)
            ).where(Country.id.in_(country_ids)).order_by(Country.id)

            result = await self.db.scalars(statement)
            return result.unique().all()
        else:
            return []

    async def get_full_list(self, *, filters: CountryFilterSchema):
        """
        Retrieve all countries, only filters can be applied
        :param filters:
        :return:
        """
        statement = select(Country).order_by(Country.id)

        if filters.name:
            statement = statement.filter(Country.name.ilike(f"%{filters.name}%"))

        statement = statement.filter(Country.available_for_order == filters.available_for_order)

        result = (await self.db.scalars(statement)).all()
        return result

    async def get_by_id(self, *, country_id: int):
        statement = select(Country).options(
            joinedload(Country.country_visas).joinedload(CountryVisa.visa_type),
        ).where(Country.id == country_id)

        result = await self.db.scalars(statement)
        return result.unique().one_or_none()

    async def update(self, *, country_id: int, data: CountryUpdateSchema) -> Country | None:
        # Update and return the country
        result = await self.db.execute(
            update(Country)
            .where(Country.id == country_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Country)
        )
        country = result.scalar_one_or_none()

        if not country:
            await self.db.rollback()
            return None

        await self.db.commit()

        # Now refresh with relationships
        await self.db.refresh(country, ["country_visas"])

        # If you need nested relationships, use a separate query
        country = await self.get_by_id(country_id=country_id)
        return country
