from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_repository
from app.database.repositories.clients import ClientsRepository
from app.exceptions import NotFoundException
from app.schemas.client import ClientFilterSchema, ClientPublicSchema, ClientListResponseSchema
from app.schemas.pagination import PageParamsSchema

router = APIRouter()


@router.get(
    path="",
    name="admin:client-list",
    response_model=ClientListResponseSchema
)
async def client_list(
        query_filters: ClientFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        clients_repository: ClientsRepository = Depends(get_repository(ClientsRepository)),
):
    result = await clients_repository.get_paginated_list(query_filters=query_filters, page_params=page_params)
    return result


@router.get(
    path="/{client_id}",
    name="admin:client-detail",
    response_model=ClientPublicSchema
)
async def client_detail(
        client_id: int,
        clients_repository: ClientsRepository = Depends(get_repository(ClientsRepository)),
):
    client = await clients_repository.get_by_id(client_id=client_id)

    if client is None:
        raise NotFoundException(detail="Client not found")

    return client
