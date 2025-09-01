from fastapi import APIRouter, Depends

from app.api.dependencies.db import get_repository
from app.api.helpers import paginate
from app.database.repositories.clients import ClientRepository
from app.exceptions import NotFoundException
from app.schemas.client import ClientFilterSchema, ClientPublicSchema
from app.schemas.pagination import PageParamsSchema
from app.schemas.pagination import PagedResponseSchema

router = APIRouter()


@router.get(
    path="/",
    name="admin:client-list",
    response_model=PagedResponseSchema
)
async def client_list(
        filters: ClientFilterSchema = Depends(),
        page_params: PageParamsSchema = Depends(),
        clients_repository: ClientRepository = Depends(get_repository(ClientRepository)),
):
    results = await clients_repository.get_list(filters=filters, page_params=page_params)
    return paginate(
        page_params,
        results,
        ClientPublicSchema
    )


@router.get(
    path="/{client_id}",
    name="admin:client-detail",
    response_model=ClientPublicSchema
)
async def client_detail(
        client_id: int,
        clients_repository: ClientRepository = Depends(get_repository(ClientRepository)),
):
    client = await clients_repository.get_by_id(client_id=client_id)

    if client is None:
        raise NotFoundException(detail="Client not found")

    return client
