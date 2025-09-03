import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, VisaDuration
from app.services import jwt_service
from tests.conftest import CountryMakerProtocol, VisaTypeMakerProtocol

pytestmark = pytest.mark.asyncio


class TestCountryVisas:
    async def test_update_invalid_id(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        country_visa_data = {
            "is_active": False,
            "visa_duration_ids": None,
        }
        response = await async_client.put(
            url=app.url_path_for(
                "admin:country_visa-update",
                country_id=1,
                country_visa_id=1
            ),
            json=country_visa_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Not found"

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
            "visa_duration_ids": None,
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
        assert response.json()["is_active"] is False
        assert response.json()["visa_type"]["id"] == visa_business.id
        assert response.json()["visa_type"]["name"] == visa_business.name
        assert response.json()["duration_data"]["attached"] is None
        assert len(response.json()["duration_data"]["available"]) == 1
        assert response.json()["duration_data"]["available"][0]["id"] == duration_1_m_s.id
        assert response.json()["duration_data"]["available"][0]["name"] == duration_1_m_s.name
        assert response.json()["duration_data"]["available"][0]["term"] == duration_1_m_s.term
        assert response.json()["duration_data"]["available"][0]["entry"] == duration_1_m_s.entry

        duration_3_m_s = await visa_duration_maker(term=VisaDuration.TERM_3, entry=VisaDuration.SINGLE_ENTRY)
        country_visa_data = {
            "is_active": True,
            "visa_duration_ids": [duration_3_m_s.id],
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
        assert response.json()["is_active"] is True
        assert response.json()["visa_type"]["id"] == visa_business.id
        assert response.json()["visa_type"]["name"] == visa_business.name
        assert len(response.json()["duration_data"]["attached"]) == 1
        assert response.json()["duration_data"]["attached"][0]["id"] == duration_3_m_s.id
        assert response.json()["duration_data"]["attached"][0]["name"] == duration_3_m_s.name
        assert response.json()["duration_data"]["attached"][0]["term"] == duration_3_m_s.term
        assert response.json()["duration_data"]["attached"][0]["entry"] == duration_3_m_s.entry
        assert len(response.json()["duration_data"]["available"]) == 1
        assert response.json()["duration_data"]["available"][0]["id"] == duration_1_m_s.id
        assert response.json()["duration_data"]["available"][0]["name"] == duration_1_m_s.name
        assert response.json()["duration_data"]["available"][0]["term"] == duration_1_m_s.term
        assert response.json()["duration_data"]["available"][0]["entry"] == duration_1_m_s.entry

        country_visa_data = {
            "visa_duration_ids": [duration_3_m_s.id, duration_1_m_s.id],
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
        assert response.json()["is_active"] is True
        assert response.json()["visa_type"]["id"] == visa_business.id
        assert response.json()["visa_type"]["name"] == visa_business.name
        assert len(response.json()["duration_data"]["attached"]) == 2
        assert response.json()["duration_data"]["attached"][0]["id"] == duration_1_m_s.id
        assert response.json()["duration_data"]["attached"][0]["name"] == duration_1_m_s.name
        assert response.json()["duration_data"]["attached"][0]["term"] == duration_1_m_s.term
        assert response.json()["duration_data"]["attached"][0]["entry"] == duration_1_m_s.entry
        assert response.json()["duration_data"]["attached"][1]["id"] == duration_3_m_s.id
        assert response.json()["duration_data"]["attached"][1]["name"] == duration_3_m_s.name
        assert response.json()["duration_data"]["attached"][1]["term"] == duration_3_m_s.term
        assert response.json()["duration_data"]["attached"][1]["entry"] == duration_3_m_s.entry
        assert response.json()["duration_data"]["available"] is None

        country_visa_data = {
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
        assert response.json()["is_active"] is True
        assert response.json()["visa_type"]["id"] == visa_business.id
        assert response.json()["visa_type"]["name"] == visa_business.name
        assert len(response.json()["duration_data"]["attached"]) == 2
        assert response.json()["duration_data"]["attached"][0]["id"] == duration_1_m_s.id
        assert response.json()["duration_data"]["attached"][0]["name"] == duration_1_m_s.name
        assert response.json()["duration_data"]["attached"][0]["term"] == duration_1_m_s.term
        assert response.json()["duration_data"]["attached"][0]["entry"] == duration_1_m_s.entry
        assert response.json()["duration_data"]["attached"][1]["id"] == duration_3_m_s.id
        assert response.json()["duration_data"]["attached"][1]["name"] == duration_3_m_s.name
        assert response.json()["duration_data"]["attached"][1]["term"] == duration_3_m_s.term
        assert response.json()["duration_data"]["attached"][1]["entry"] == duration_3_m_s.entry
        assert response.json()["duration_data"]["available"] is None
