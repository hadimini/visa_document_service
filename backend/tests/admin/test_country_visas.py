import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.visa_durations import VisaDurationsRepository
from app.models import User, VisaDuration
from app.services import jwt_service
from tests.conftest import CountryMakerProtocol, VisaTypeMakerProtocol

pytestmark = pytest.mark.asyncio


class TestCountryVisas:

    async def test_update_country_visa_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            country_maker: CountryMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            country_visa_maker,
            visa_duration_maker
    ) -> None:
        russia = await country_maker(name="Russia", alpha2="RU", alpha3="RUS")
        visa_business = await visa_type_maker(name="Business")
        russia_business_visa = await country_visa_maker(country_id=russia.id, visa_type_id=visa_business.id)
        duration_1_m_s = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)

        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        country_visa_data = {
            "is_active": False,
            "visa_duration_ids": [duration_1_m_s.id],
        }
        response = await async_client.put(
            url=app.url_path_for(
                "admin:country_visa-update",
                country_id=russia.id,
                country_visa_id=visa_business.id
            ),
            json=country_visa_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == russia_business_visa.id
        assert response.json()["visa_type"]["id"] == visa_business.id
        assert response.json()["visa_type"]["name"] == visa_business.name
        assert response.json()["visa_durations"] == [
            {
                "id": duration_1_m_s.id,
                "name": duration_1_m_s.name,
            }
        ]
