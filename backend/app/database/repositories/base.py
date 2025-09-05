from typing import Any, TypeVar, Type

from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination import PageParamsSchema


ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db


class BasePaginatedRepository(BaseRepository):
    def __init__(self, db: AsyncSession, model: Type[ModelType]) -> None:
        super().__init__(db)
        self.model = model

    async def paginate(
            self,
            query,
            page_params: PageParamsSchema,
    ) -> dict[str, Any]:
        """Paginate the query"""
        page = page_params.page
        size = page_params.size

        total = await self.db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        items_result = await self.db.execute(
            query.offset((page - 1) * size).limit(size)
        )
        items = items_result.scalars().all()

        total_pages = (total + size - 1) // size if total else 0
        has_next = page < total_pages
        has_prev = page > 1

        result = dict(
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            items=items,
        )
        return result
