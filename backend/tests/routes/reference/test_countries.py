import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.countries import CountriesRepository
from app.models import Country, User
from app.schemas.country import CountryFilterSchema, CountryUpdateSchema, CountryReferencePublicSchema
from app.services import jwt_service


pytestmark = pytest.mark.asyncio


class TestCountries:

    async def test_country_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
            load_countries
    ):
        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None
        token = token_pair.access

        response = await async_client.get(
            app.url_path_for("reference:country-list"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 212

        countries_repo = CountriesRepository(async_db)
        countries_in_db = await countries_repo.get_full_list(
            query_filters=CountryFilterSchema(
                name=""
            )
        )
        results = [
            CountryReferencePublicSchema.model_validate(c).model_dump()
            for c in countries_in_db
        ]
        assert response.json() == results

    async def test_country_list_name_filter(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
            load_countries
    ):
        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None
        token = token_pair.access

        response = await async_client.get(
            app.url_path_for("reference:country-list"),
            params={"name": "russia"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json() == [
            {
                "MODEL_TYPE": Country.get_model_type(),
                "id": 160,
                "name": "Russian Federation",
                "alpha2": "RU",
                "alpha3": "RUS",
                "available_for_order": False,
            }
        ]

    async def test_country_list_available_for_order_filter(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
            load_countries
    ):
        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None
        token = token_pair.access

        countries_repo = CountriesRepository(async_db)
        await countries_repo.update(country_id=1, data=CountryUpdateSchema(available_for_order=True))
        response = await async_client.get(
            app.url_path_for("reference:country-list"),
            params={"available_for_order": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json() == [
            {
                "MODEL_TYPE": Country.get_model_type(),
                "id": 1,
                "name": "Afghanistan",
                "alpha2": "AF",
                "alpha3": "AFG",
                "available_for_order": True,
            }
        ]
