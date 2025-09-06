from typing import Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models import CountryVisa, VisaType
from app.models.countries import Country
from app.schemas.country import CountryFilterSchema, CountryUpdateSchema
from app.schemas.pagination import PageParamsSchema


class CountriesRepository(BasePaginatedRepository, BuildFiltersMixin):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=Country)

    def build_filters(self, *, query_filters: CountryFilterSchema) -> list:
        filters: list[ClauseElement] = list()

        if query_filters.name:
            filters.append(Country.name.ilike(f"%{query_filters.name}%"))

        if query_filters.available_for_order:
            filters.append(
                Country.available_for_order == query_filters.available_for_order
            )
        return filters

    async def get_paginated_list(
            self, *, query_filters: CountryFilterSchema, page_params: PageParamsSchema
    ) -> dict[str, Any]:
        statement = select(Country)

        if filters := self.build_filters(query_filters=query_filters):
            statement = statement.where(and_(*filters))

        statement = statement.order_by(Country.id)
        result = await self.paginate(statement, page_params)
        return result

    async def get_full_list(self, *, query_filters: CountryFilterSchema):
        """
        Retrieve all countries, only filters can be applied
        :param filters:
        :return:
        """
        statement = select(Country).order_by(Country.id)

        if filters := self.build_filters(query_filters=query_filters):
            statement = statement.where(and_(*filters))

        result = (await self.db.scalars(statement)).all()
        return result

    async def get_by_id(self, *, country_id: int, populate_visa_data: bool = False):
        statement = select(Country).options(
            selectinload(Country.country_visas).selectinload(CountryVisa.visa_type),
        ).where(Country.id == country_id)

        result = await self.db.scalars(statement)
        country = result.one_or_none()

        if not country:
            return None

        if populate_visa_data:
            attached_ids = [
                vc.visa_type.id for vc in country.country_visas
            ]

            available_statement = select(VisaType)

            if attached_ids:
                available_statement = available_statement.where(VisaType.id.notin_(attached_ids))

            available_visa_types = (
                await self.db.scalars(
                    available_statement.order_by(VisaType.id)
                )
            ).all()
            country.visa_data = {
                "attached": country.country_visas or None,
                "available": available_visa_types or None
            }

        return country

    async def update(self, *, country_id: int, data: CountryUpdateSchema) -> Country | None:
        country = await self.get_by_id(country_id=country_id)

        if not country:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"visa_type_ids"})
        for field, value in update_data.items():
            setattr(country, field, value)

        # Handle data.visa_type_ids relationships if provided
        if data.visa_type_ids is not None:
            current_visa_ids = {cv.visa_type_id for cv in country.country_visas}
            new_visa_ids = set(data.visa_type_ids)

            # Remove relationships that are no longer needed
            visas_to_remove = [
                cv for cv in country.country_visas if cv.visa_type_id not in new_visa_ids
            ]

            for visa in visas_to_remove:
                await self.db.delete(visa)

            # Add new relationships
            visas_to_add = new_visa_ids - current_visa_ids

            for visa_type_id in visas_to_add:
                country_visa = CountryVisa(
                    country_id=country_id,
                    visa_type_id=visa_type_id,
                    is_active=True
                )
                self.db.add(country_visa)
        await self.db.commit()

        # Refresh with relationships
        await self.db.refresh(country, ["country_visas"])

        # If you need nested relationships, use a separate query
        country = await self.get_by_id(country_id=country_id, populate_visa_data=True)
        return country
