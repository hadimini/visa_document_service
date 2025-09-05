from mypy.build import Sequence
from pydantic import BaseModel

from app.schemas.pagination import PageParamsSchema, PagedResponseSchema


def paginate(
        page_params: PageParamsSchema,
        results: Sequence,
        ResponseSchema: BaseModel
) -> PagedResponseSchema:
    """Paginate the query"""

    page = page_params.page
    total = len(results)
    size = page_params.size
    total_pages = (total + size - 1) // size if total else 0
    has_next = page < total_pages
    has_prev = page > 1

    return PagedResponseSchema(
        page=page,
        size=size,
        total=len(results),
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        results=[ResponseSchema.model_validate(item) for item in results],
    )
