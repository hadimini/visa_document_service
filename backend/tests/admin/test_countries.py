import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.database.repositories.countries import CountriesRepository
from app.models import CountryVisa, VisaType
from app.models.audit import LogEntry
from app.models.countries import Country
from app.models.users import User
from app.services import jwt_service
from tests.conftest import CountryMakerProtocol, VisaTypeMakerProtocol, country_visa_maker

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
        assert response.json().get("size") == 25
        assert response.json().get("results") == [
            {
                "id": 160,
                "name": "Russian Federation",
                "alpha2": "RU",
                "alpha3": "RUS",
                "available_for_order": False,
                "visa_data": None,
                "MODEL_TYPE": Country.get_model_type(),
            }
        ]

    async def test_country_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            country_maker: CountryMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            country_visa_maker,
    ):
        russia = await country_maker(name="russia", alpha2="RU", alpha3="RUS")
        visa_business = await visa_type_maker(name="Business")
        visa_tourist = await visa_type_maker(name="Tourist")
        russia_business_visa = await country_visa_maker(country_id=russia.id, visa_type_id=visa_business.id)

        token_pair = jwt_service.create_token_pair(user=test_admin)
        token = token_pair.access
        response = await async_client.get(
            app.url_path_for("admin:country-detail", country_id=russia.id),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == russia.id
        assert response.json().get("name") == russia.name
        assert response.json().get("alpha2") == russia.alpha2
        assert response.json().get("alpha3") == russia.alpha3
        assert response.json().get("available_for_order") == russia.available_for_order
        assert response.json().get("visa_data") == {
            "attached": [
                {
                    "MODEL_TYPE": CountryVisa.get_model_type(),
                    "id": russia_business_visa.id,
                    "is_active": True,
                    "visa_type": {
                        "MODEL_TYPE": VisaType.get_model_type(),
                        "id": visa_business.id,
                        "name": visa_business.name,
                    }
                }
            ],
            "available": [
                {
                    "MODEL_TYPE": VisaType.get_model_type(),
                    "id": visa_tourist.id,
                    "name": visa_tourist.name,
                }
            ]
        }

    async def test_country_detail_not_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_admin: User,
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        token = token_pair.access
        response = await async_client.get(
            app.url_path_for("admin:country-detail", country_id=1),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_country_update_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            visa_type_maker: VisaTypeMakerProtocol,
            load_countries,
    ):
        audit_repo = AuditRepository(async_db)
        countries_repo = CountriesRepository(async_db)
        country = await countries_repo.get_by_id(country_id=1)
        assert country.available_for_order is False

        visa_business = await visa_type_maker(name="Business")
        visa_tourist = await visa_type_maker(name="Tourist")

        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        # Attach visa types
        update_data = {
            "available_for_order": True,
            "visa_type_ids": [visa_business.id, visa_tourist.id],
        }

        response = await async_client.put(
            app.url_path_for("admin:country-update", country_id=country.id),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == 1
        assert response.json().get("available_for_order") is True

        assert response.json().get("visa_data")["available"] is None
        assert response.json().get("visa_data")["attached"][0]["is_active"] is True
        assert response.json().get("visa_data")["attached"][0]["visa_type"]["id"] == visa_business.id
        assert response.json().get("visa_data")["attached"][0]["visa_type"]["name"] == visa_business.name
        assert response.json().get("visa_data")["attached"][1]["is_active"] is True
        assert response.json().get("visa_data")["attached"][1]["visa_type"]["id"] == visa_tourist.id
        assert response.json().get("visa_data")["attached"][1]["visa_type"]["name"] == visa_tourist.name

        # Remove 1 visa type

        update_data = {
            "available_for_order": True,
            "visa_type_ids": [visa_business.id],
        }

        response = await async_client.put(
            app.url_path_for("admin:country-update", country_id=country.id),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == 1
        assert response.json().get("available_for_order") is True

        assert response.json().get("visa_data")["attached"][0]["is_active"] is True
        assert response.json().get("visa_data")["attached"][0]["visa_type"]["id"] == visa_business.id
        assert response.json().get("visa_data")["attached"][0]["visa_type"]["name"] == visa_business.name

        assert response.json().get("visa_data")["available"][0]["id"] == visa_tourist.id
        assert response.json().get("visa_data")["available"][0]["name"] == visa_tourist.name

        # Remove all visa types

        update_data = {
            "available_for_order": True,
            "visa_type_ids": []
        }
        response = await async_client.put(
            app.url_path_for("admin:country-update", country_id=country.id),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == 1
        assert response.json().get("available_for_order") is True
        assert response.json().get("visa_data")["attached"] is None
        assert response.json().get("visa_data")["available"][0]["id"] == visa_business.id
        assert response.json().get("visa_data")["available"][0]["name"] == visa_business.name
        assert response.json().get("visa_data")["available"][1]["id"] == visa_tourist.id
        assert response.json().get("visa_data")["available"][1]["name"] == visa_tourist.name


        log_entries = await audit_repo.get_for_user(user_id=test_admin.id)
        assert len(log_entries) == 3

        for log_entry in log_entries:
            assert log_entry.user_id == test_admin.id
            assert log_entry.action == LogEntry.ACTION_UPDATE
            assert log_entry.model_type == Country.get_model_type()
            assert log_entry.target_id == country.id

    async def test_country_update_invalid_id(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            load_countries,
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        update_data = {
            "available_for_order": True
        }
        response = await async_client.put(
            app.url_path_for("admin:country-update", country_id=1000),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Not found"
