from typing import Any, Optional, TypeVar, Type, Generic

from sqlalchemy import select, func, and_
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from app.schemas.pagination import PageParamsSchema


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
FilterSchemaType = TypeVar("FilterSchemaType")


class BaseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db


class BasePaginatedRepository(BaseRepository, Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]) -> None:
        super().__init__(db)
        self.model = model

    async def get_paginated_list(
            self,
            *,
            query_filters: Optional[FilterSchemaType] = None,
            page_params: PageParamsSchema,
            additional_filters: Optional[list[ClauseElement]] = None,
            order_by: Optional[Any] = None,
            options: Optional[list] = None
    ) -> dict[str, Any]:
        """
        Generic paginated list method

        Args:
            query_filters: Filter shema object
            page_params: Pagination parameters
            additional_filters: Extra SQLAlchemy filters
            order_by: Ordering criteria (defaults to model.id)
            options: SQLAlchemy options like selectinload, joinedload
        """
        statement = select(self.model)

        # Apply options like selectinload, joinedload
        if options:
            statement = statement.options(*options)

        # Build filters from query_filters if the repository has build filters method
        filters = []

        if hasattr(self, "build_filters") and query_filters:
            filters.extend(self.build_filters(query_filters=query_filters))

        # Add any additional filters
        if additional_filters:
            filters.extend(additional_filters)

        # Apply filters
        if filters:
            statement = statement.where(and_(*filters))

        # Apply ordering
        if order_by is not None:
            statement = statement.order_by(order_by)
        else:
            statement = statement.order_by(self.model.id)

        return await self.paginate(query=statement, page_params=page_params)

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
