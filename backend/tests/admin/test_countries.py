import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.services import jwt_service


pytestmark = pytest.mark.asyncio


class TestCountries:

    async def test_country_list(
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

    async def test_country_list_filters(
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
            params={"name": "russia"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("total") == 1
        assert response.json().get("page") == 1
        assert response.json().get("size") == 10
        assert response.json().get("results") == [
            {
                "id": 160,
                "name": "Russian Federation",
                "alpha2": "RU",
                "alpha3": "RUS",
                "available_for_order": False,
            }
        ]

    async def test_country_detail(
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
            app.url_path_for("admin:country-detail", country_id=1),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == 1
        assert response.json().get("name") == "Afghanistan"
        assert response.json().get("alpha2") == "AF"
        assert response.json().get("alpha3") == "AFG"
        assert response.json().get("available_for_order") == False
