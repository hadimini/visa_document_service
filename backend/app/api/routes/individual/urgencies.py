from fastapi import APIRouter

from app.api.routes.base.urgencies import urgency_list
from app.schemas.urgencies import UrgencyPublicSchema

router = APIRouter()


urgency_list = router.get(
    path="/",
    response_model=list[UrgencyPublicSchema],
    name="individual:urgency-list"
)(urgency_list)
