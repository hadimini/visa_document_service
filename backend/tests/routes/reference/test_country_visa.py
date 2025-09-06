import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.services import jwt_service
from tests.conftest import VisaTypeMakerProtocol, CountryMakerProtocol


pytestmark = pytest.mark.asyncio


class TestCountryVisa:
    async def test_authentication_required(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
            country_maker: CountryMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            country_visa_maker
    ) -> None:
        response = await async_client.get(
            app.url_path_for("reference:country-visa-type-list", country_id=1),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    async def test_country_visa_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
            country_maker: CountryMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            country_visa_maker
    ) -> None:

        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None

        country = await country_maker(
            name="Russia",
            alpha2="RU",
            alpha3="RUS",
            available_for_order=True,
        )
        visa_type = await visa_type_maker(
            name="Business"
        )
        country_visa_maker = await country_visa_maker(
            country_id=country.id,
            visa_type_id=visa_type.id,
            is_active=True,
        )

        response = await async_client.get(
            app.url_path_for("reference:country-visa-type-list", country_id=country.id),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == country_visa_maker.id
        assert response.json()[0]["is_active"] == country_visa_maker.is_active
        assert response.json()[0]["visa_type"]["id"] == visa_type.id
        assert response.json()[0]["visa_type"]["name"] == visa_type.name
