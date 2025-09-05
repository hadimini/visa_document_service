from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_repository
from app.database.repositories.clients import ClientRepository
from app.exceptions import NotFoundException
from app.schemas.client import ClientFilterSchema, ClientResponseSchema, ClientListResponseSchema
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
        clients_repository: ClientRepository = Depends(get_repository(ClientRepository)),
):
    result = await clients_repository.get_list(query_filters=query_filters, page_params=page_params)
    return result


@router.get(
    path="/{client_id}",
    name="admin:client-detail",
    response_model=ClientResponseSchema
)
async def client_detail(
        client_id: int,
        clients_repository: ClientRepository = Depends(get_repository(ClientRepository)),
):
    client = await clients_repository.get_by_id(client_id=client_id)

    if client is None:
        raise NotFoundException(detail="Client not found")

    return client
