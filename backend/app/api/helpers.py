from pydantic import BaseModel
from app.schemas.core import CoreSchema
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema


def paginate(
        page_params: PageParamsSchema,
        results: list,
        ResponseSchema: BaseModel
) -> PagedResponseSchema:
    """Paginate the query"""

    return PagedResponseSchema(
        page=page_params.page,
        size=page_params.size,
        total=len(results),
        results=[ResponseSchema.model_validate(item) for item in results],
    )
