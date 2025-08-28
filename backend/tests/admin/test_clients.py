import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.services import jwt_service

pytestmark = pytest.mark.asyncio


class TestClients:
    async def test_list_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            test_individual
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:client-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )
        assert response.status_code == 200
        assert len(response.json()["results"]) == 1
        print("\n\n\n", response.json()["results"][0])
