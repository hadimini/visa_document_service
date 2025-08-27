from fastapi import APIRouter
from app.api.routes.base.countries import country_list, country_detail

from app.schemas.pagination import PagedResponseSchema
from app.schemas.country import CountryPublicSchema

router = APIRouter()


country_list = router.get(
    path="/",
    response_model=PagedResponseSchema,
    name="individual:country-list"
)(country_list)

country_detail = router.get(
    path="/{country_id}",
    response_model=CountryPublicSchema,
    name="individual:country-detail"
)(country_detail)
