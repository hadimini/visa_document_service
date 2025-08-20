from typing import Annotated, Generic, TypeVar
from pydantic import conint
from pydantic.generics import GenericModel

from app.schemas.core import CoreSchema

TypeT = TypeVar("T")


class PageParamsSchema(CoreSchema):
    page: Annotated[int, conint(ge=1)] = 1
    size: Annotated[int, conint(ge=1, le=100)] = 10


class PagedResponseSchema(CoreSchema, Generic[TypeT]):
    total: int
    page: int
    size: int
    results: list[TypeT]
