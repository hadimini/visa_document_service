from fastapi import APIRouter

from app.api.routes.base.clients import client_detail, client_list
from app.schemas.client import ClientPublicSchema
from app.schemas.pagination import PagedResponseSchema

router = APIRouter()


client_list = router.get(
    path="/",
    name="admin:client-list",
    response_model=PagedResponseSchema
)(client_list)


client_detail = router.get(
    path="/{client_id}",
    name="admin:client-detail",
    response_model=ClientPublicSchema
)(client_detail)
