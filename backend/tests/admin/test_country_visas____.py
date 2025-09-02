# import pytest
# from fastapi import FastAPI, status
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.database.repositories.audit import AuditRepository
# from app.models.audit import LogEntry
# from app.models.countries import Country
# from app.models.country_visas import CountryVisa
# from app.models.users import User
# from app.models.visa_types import VisaType
# from app.services import jwt_service
# from tests.conftest import CountryMakerProtocol, VisaTypeMakerProtocol
#
# pytestmark = pytest.mark.asyncio
#
#
# class TestCountryVisa:
#     async def test_list_success(
#             self,
#             app: FastAPI,
#             async_client: AsyncClient,
#             async_db: AsyncSession,
#             test_admin: User,
#             country_maker: CountryMakerProtocol,
#             visa_type_maker: VisaTypeMakerProtocol,
#             country_visa_maker,
#     ) -> None:
#         russia: Country = await country_maker(
#             name="Russia",
#             alpha2="RU",
#             alpha3="RUS",
#         )
#         visa_business: VisaType = await visa_type_maker(name="Business")
#         country_visa = await country_visa_maker(
#             country_id=russia.id,
#             visa_type_id=visa_business.id,
#             is_active=True,
#         )
#
#         token_pair = jwt_service.create_token_pair(user=test_admin)
#         assert token_pair is not None
#
#         response = await async_client.get(
#             url=app.url_path_for("admin:country_visa-list"),
#             headers={"Authorization": f"Bearer {token_pair.access}"},
#         )
#         assert response.status_code == 200
#         assert len(response.json()) == 1
#         response.json()[0]["id"] = country_visa.id
#         response.json()[0]["country_id"] = country_visa.country_id
#         response.json()[0]["visa_type_id"] = country_visa.visa_type_id
#
#     async def test_detail_success(
#             self,
#             app: FastAPI,
#             async_client: AsyncClient,
#             async_db: AsyncSession,
#             test_admin: User,
#             country_maker: CountryMakerProtocol,
#             visa_type_maker: VisaTypeMakerProtocol,
#             country_visa_maker,
#     ) -> None:
#         russia: Country = await country_maker(
#             name="Russia",
#             alpha2="RU",
#             alpha3="RUS",
#         )
#         visa_business: VisaType = await visa_type_maker(name="Business")
#         country_visa = await country_visa_maker(
#             country_id=russia.id,
#             visa_type_id=visa_business.id,
#             is_active=True,
#         )
#
#         token_pair = jwt_service.create_token_pair(user=test_admin)
#         assert token_pair is not None
#
#         response = await async_client.get(
#             url=app.url_path_for("admin:country_visa-detail", country_visa_id=country_visa.id),
#             headers={"Authorization": f"Bearer {token_pair.access}"},
#         )
#
#         assert response.status_code == 200
#         response.json()["id"] = country_visa.id
#         response.json()["country_id"] = country_visa.country_id
#         response.json()["visa_type_id"] = country_visa.visa_type_id
#
#     async def test_detail_error_not_found(
#             self,
#             app: FastAPI,
#             async_client: AsyncClient,
#             async_db: AsyncSession,
#             test_admin: User,
#     ):
#         token_pair = jwt_service.create_token_pair(user=test_admin)
#         assert token_pair is not None
#
#         response = await async_client.get(
#             url=app.url_path_for("admin:country_visa-detail", country_visa_id=1000),
#             headers={"Authorization": f"Bearer {token_pair.access}"},
#         )
#         assert response.status_code == status.HTTP_404_NOT_FOUND
#         assert response.json().get("detail") == "Not found"
#
#     async def test_create_success(
#             self,
#             app: FastAPI,
#             async_client: AsyncClient,
#             async_db: AsyncSession,
#             country_maker: CountryMakerProtocol,
#             visa_type_maker: VisaTypeMakerProtocol,
#             test_admin: User,
#     ) -> None:
#         russia: Country = await country_maker(
#             name="Russia",
#             alpha2="RU",
#             alpha3="RUS",
#         )
#         visa_business: VisaType = await visa_type_maker(name="Business")
#         token_pair = jwt_service.create_token_pair(user=test_admin)
#         assert token_pair is not None
#         country_visa_data = {
#             "country_id": russia.id,
#             "visa_type_id": visa_business.id,
#             "is_active": True
#         }
#
#         response = await async_client.post(
#             url=app.url_path_for("admin:country_visa-create"),
#             headers={"Authorization": f"Bearer {token_pair.access}"},
#             json=country_visa_data
#         )
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.json()["country_id"] == russia.id
#         assert response.json()["visa_type_id"] == visa_business.id
#
#         audit_repo = AuditRepository(async_db)
#         log_entries = await audit_repo.get_for_user(user_id=test_admin.id)
#         assert len(log_entries) == 1
#         assert log_entries[0].user_id == test_admin.id
#         assert log_entries[0].action == LogEntry.ACTION_CREATE
#         assert log_entries[0].model_type == CountryVisa.get_model_type()
#         assert log_entries[0].target_id == response.json()["id"]
#
#     async def test_create_error_already_exists(
#             self,
#             app: FastAPI,
#             async_client: AsyncClient,
#             async_db: AsyncSession,
#             test_admin: User,
#             country_maker: CountryMakerProtocol,
#             visa_type_maker: VisaTypeMakerProtocol,
#             country_visa_maker
#     ) -> None:
#         russia: Country = await country_maker(
#             name="Russia",
#             alpha2="RU",
#             alpha3="RUS",
#         )
#         visa_business: VisaType = await visa_type_maker(name="Business")
#         await country_visa_maker(
#             country_id=russia.id,
#             visa_type_id=visa_business.id,
#             is_active=True,
#         )
#         token_pair = jwt_service.create_token_pair(user=test_admin)
#         assert token_pair is not None
#         country_visa_data = {
#             "country_id": russia.id,
#             "visa_type_id": visa_business.id,
#             "is_active": True
#         }
#
#         response = await async_client.post(
#             url=app.url_path_for("admin:country_visa-create"),
#             headers={"Authorization": f"Bearer {token_pair.access}"},
#             json=country_visa_data
#         )
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert response.json()["detail"] == "Object already exists"
