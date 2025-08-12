import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.users import UsersRepository

pytestmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_route_exist(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.get(app.url_path_for("users:user-list"))
        assert response.status_code == status.HTTP_200_OK


class TestCreate:
    async def test_create_user_success(
            self,
            app: FastAPI,
            client: AsyncClient,
            db: AsyncSession,
    ):
        user_rpo = UsersRepository(db)
        user_data = {
            "email": "testuser5@example.com",
            "name": "user1",
            "password": "samplepassword"
        }

        response = await client.post(
            app.url_path_for("users:users-create"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        user_in_db = await user_rpo.get_by_email(email=user_data["email"])
        assert user_in_db is not None
        assert user_in_db.name == user_data["name"]
