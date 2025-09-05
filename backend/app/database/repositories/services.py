from typing import Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.repositories.base import BaseRepository
from app.models import Service
from app.schemas.pagination import PageParamsSchema
from app.schemas.service import ServiceCreateSchema, ServiceFilterSchema


class ServicesRepository(BaseRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    def build_service_filters(self, *, query_filters: ServiceFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions"""
        filters = list()

        if query_filters.name:
            filters.append(Service.name.ilike(f"%{query_filters.name}%"))

        if query_filters.fee_type:
            filters.append(Service.fee_type == query_filters.fee_type)
            # filters.append(Service.fee_type == query_filters.fee_type.value)

        if query_filters.country_id:
            filters.append(Service.country_id == query_filters.country_id)

        if query_filters.urgency_id:
            filters.append(Service.urgency_id == query_filters.urgency_id)

        if query_filters.visa_duration_id:
            filters.append(Service.visa_duration_id == query_filters.visa_duration_id)

        if query_filters.visa_type_id:
            filters.append(Service.visa_type_id == query_filters.visa_type_id)

        return filters

    async def get_list(self, *, query_filters: ServiceFilterSchema, page_params: PageParamsSchema) -> Sequence[Service]:
        statement = select(Service)
        filters = self.build_service_filters(query_filters=query_filters)

        if filters:
            statement = statement.where(and_(*filters))

        statement = statement.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
        return (await self.db.scalars(statement)).all()

    async def get_by_id(self, *, service_id) -> Service:
        # options = [joinedload(Service.tariff)]  # todo

        statement = select(Service).where(Service.id == service_id)
        return (
            await self.db.scalars(statement)
        ).one_or_none()

    async def create(self, *, data: ServiceCreateSchema) -> Service:
        service = Service(**data.model_dump())
        self.db.add(service)
        await self.db.commit()
        return service
