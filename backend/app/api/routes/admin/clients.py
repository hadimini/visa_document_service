from fastapi import APIRouter

from app.api.routes.base.clients import client_list
from app.schemas.pagination import PagedResponseSchema

router = APIRouter()


client_list = router.get(
    path="/",
    name="admin:client-list",
    response_model=PagedResponseSchema
)(client_list)
