from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.models.visa_types import VisaType
from app.exceptions import NameExistsException, NotFoundException
from app.schemas.pagination import PageParamsSchema
from app.schemas.visa_type import VisaTypeCreateSchema, VisaTypeUpdateSchema


class VisaTypesRepository(BasePaginatedRepository, BuildFiltersMixin):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=VisaType)

    def build_filters(self, *, query_filters) -> list:
        # TODO
        return []

    async def get_paginated_list(
            self, *, query_filters, page_params: PageParamsSchema
    ) -> dict[str, Any]:
        statement = select(VisaType)

        if filters := self.build_filters(query_filters=query_filters):
            statement = statement.where(*filters)

        statement = statement.order_by(VisaType.id)
        return await self.paginate(statement, page_params)

    async def get_by_id(self, *, visa_type_id: int) -> VisaType | None:
        statement = select(VisaType).where(VisaType.id == visa_type_id)
        result = await self.db.scalars(statement)
        return result.one_or_none()

    async def get_by_name(self, *, name: str) -> VisaType | None:
        statement = select(VisaType).where(VisaType.name == name)
        result = await self.db.execute(statement)
        visa_type = result.scalars().one_or_none()
        return visa_type

    async def create(self, *, data: VisaTypeCreateSchema) -> VisaType:
        visa_type = VisaType(**data.model_dump())

        if await self.get_by_name(name=visa_type.name) is not None:
            raise NameExistsException()

        self.db.add(visa_type)
        await self.db.commit()
        return visa_type

    async def update(self, *, visa_type_id: int, data: VisaTypeUpdateSchema) -> VisaType | None:
        visa_type = await self.get_by_id(visa_type_id=visa_type_id)

        if not visa_type:
            raise NotFoundException()

        for attr, value in data.model_dump().items():
            setattr(visa_type, attr, value)
        await self.db.commit()
        await self.db.refresh(visa_type)
        return visa_type
