import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.users import UsersRepository

pytestmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_route_exist(self, app: FastAPI, async_client: AsyncClient) -> None:
        response = await async_client.get(app.url_path_for("users:user-list"))
        assert response.status_code == status.HTTP_200_OK


class TestCreate:
    async def test_create_user_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
    ):
        user_rpo = UsersRepository(async_db)
        user_data = {
            "email": "testuser2@example.com",
            "name": "user2",
            "password": "samplepassword"
        }

        response = await async_client.post(
            app.url_path_for("users:users-create"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        user_in_db = await user_rpo.get_by_email(email=user_data["email"])
        assert user_in_db is not None
        assert user_in_db.name == user_data["name"]
