import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.countries import Country
from app.models.users import User
from app.services import jwt_service


pytestmark = pytest.mark.asyncio


class TestCountries:
    async def test_get_countries(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            load_countries
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        token = token_pair.access

        response = await async_client.get(
            app.url_path_for("admin:country-list"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
