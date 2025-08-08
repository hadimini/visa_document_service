from fastapi import APIRouter

from app.models.users import User


router = APIRouter()


@router.get("/", response_model=list, name="users:user-list")
async def get_users():
    return [
        {
            "id": 1,
            "name": "Charlie Mini"
        }
    ]
