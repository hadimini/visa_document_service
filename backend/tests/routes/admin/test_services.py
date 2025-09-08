from decimal import Decimal

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.models import LogEntry, Service, User, tariff_services, Tariff, TariffService
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.service import FeeTypeEnum, TariffServiceCreateSchema
from app.services import jwt_service


class TestServicesRoutes:

    @pytest.mark.asyncio
    async def test_paginated_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            service_maker
    ) -> None:
        services = [
            await service_maker(fee_type=FeeTypeEnum.CONSULAR)
            for _ in range(2)
        ]
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:service-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "page": 1,
            "size": 25,
            "total": 2,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
            "items": [
                {
                    "MODEL_TYPE": Service.get_model_type(),
                    "name": services[0].name,
                    "fee_type": services[0].fee_type,
                    "country_id": None,
                    "urgency_id": None,
                    "visa_duration_id": None,
                    "visa_type_id": None,
                    "id": services[0].id,
                    "updated_at": services[0].updated_at.strftime(STRFTIME_FORMAT),
                    "created_at": services[0].created_at.strftime(STRFTIME_FORMAT),
                    "archived_at": None,
                    "tariff_services": []
                }, {
                    "MODEL_TYPE": Service.get_model_type(),
                    "name": services[1].name,
                    "fee_type": services[1].fee_type,
                    "country_id": None,
                    "urgency_id": None,
                    "visa_duration_id": None,
                    "visa_type_id": None,
                    "id": services[1].id,
                    "updated_at": services[1].updated_at.strftime(STRFTIME_FORMAT),
                    "created_at": services[1].created_at.strftime(STRFTIME_FORMAT),
                    "archived_at": None,
                    "tariff_services": []
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_paginated_list_with_filters(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            service_maker
    ) -> None:
        services = [
            await service_maker(fee_type=FeeTypeEnum.CONSULAR)
            for _ in range(2)
        ]
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None
        response = await async_client.get(
            url=app.url_path_for("admin:service-list"),
            params={"name": services[0].name, "fee_type": services[0].fee_type},
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "page": 1,
            "size": 25,
            "total": 1,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False,
            "items": [
                {
                    "MODEL_TYPE": Service.get_model_type(),
                    "name": services[0].name,
                    "fee_type": services[0].fee_type,
                    "country_id": None,
                    "urgency_id": None,
                    "visa_duration_id": None,
                    "visa_type_id": None,
                    "id": services[0].id,
                    "updated_at": services[0].updated_at.strftime(STRFTIME_FORMAT),
                    "created_at": services[0].created_at.strftime(STRFTIME_FORMAT),
                    "archived_at": None,
                    "tariff_services": []
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_get_by_id_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            service_maker
    ) -> None:
        service = await service_maker(fee_type=FeeTypeEnum.CONSULAR)
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None
        response = await async_client.get(
            url=app.url_path_for("admin:service-detail", service_id=service.id),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "MODEL_TYPE": Service.get_model_type(),
            "name": service.name,
            "fee_type": service.fee_type,
            "country_id": None,
            "urgency_id": None,
            "visa_duration_id": None,
            "visa_type_id": None,
            "id": service.id,
            "updated_at": service.updated_at.strftime(STRFTIME_FORMAT),
            "created_at": service.created_at.strftime(STRFTIME_FORMAT),
            "archived_at": None,
            "tariff_services": []
        }

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            service_maker
    ) -> None:
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None
        response = await async_client.get(
            url=app.url_path_for("admin:service-detail", service_id=1000),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_service(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
    ) -> None:
        """Test service creation"""
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None
        data = {
            "name": "Test Service",
            "fee_type": FeeTypeEnum.GENERAL,
        }
        response = await async_client.post(
            url=app.url_path_for("admin:service-create"),
            json=data,
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["MODEL_TYPE"] == Service.get_model_type()
        assert response.json()["name"] == data["name"]
        assert response.json()["fee_type"] == data["fee_type"]

        audit_repo = AuditRepository(db=async_db)
        logs = await audit_repo.get_for_user(user_id=test_admin.id)

        assert len(logs) == 1
        assert logs[0].user_id == test_admin.id
        assert logs[0].action == LogEntry.ACTION_CREATE
        assert logs[0].model_type == Service.get_model_type()
        assert logs[0].target_id == response.json().get("id")

    @pytest.mark.asyncio
    async def test_update_service(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            test_tariff: Tariff,
            service_maker,
    ) -> None:
        """Test service update"""
        service = await service_maker(
            fee_type=FeeTypeEnum.GENERAL,
            tariff_services=[
                TariffServiceCreateSchema(
                    price=Decimal(10),
                    tax=Decimal(0.10),
                    tariff_id=test_tariff.id,
                )
            ]
        )
        price = Decimal(20.5)
        tax = Decimal(20.5)
        tax_amount = price * tax

        update_data = {
            "name": "Updated Test Service",
            "fee_type": FeeTypeEnum.CONSULAR,
            "tariff_services": [
                {
                    "price": str(price),
                    "tax": str(tax),
                    "tariff_id": test_tariff.id,
                }

            ]
        }
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.put(
            url=app.url_path_for("admin:service-update", service_id=service.id),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == service.id
        assert response.json()["MODEL_TYPE"] == Service.get_model_type()
        assert response.json()["name"] == update_data["name"]
        assert response.json()["fee_type"] == update_data["fee_type"]
        assert response.json()["country_id"] is None
        assert response.json()["urgency_id"] is None
        assert response.json()["visa_duration_id"] is None
        assert response.json()["visa_type_id"] is None

        r_tariff_services = response.json()["tariff_services"]
        assert len(r_tariff_services) == 1
        assert r_tariff_services[0]["MODEL_TYPE"] == TariffService.get_model_type()
        assert r_tariff_services[0]["price"] == str(price)
        assert r_tariff_services[0]["tax"] == str(tax)
        assert r_tariff_services[0]["tax_amount"] == str(tax_amount)
        assert r_tariff_services[0]["total"] == str(price + tax_amount)
        assert r_tariff_services[0]["tariff"] == {
            "MODEL_TYPE": Tariff.get_model_type(),
            "id": test_tariff.id,
            "name": test_tariff.name,
            "is_default": test_tariff.is_default,
        }

        audit_repo = AuditRepository(db=async_db)
        logs = await audit_repo.get_for_user(user_id=test_admin.id)

        assert len(logs) == 1
        assert logs[0].user_id == test_admin.id
        assert logs[0].action == LogEntry.ACTION_UPDATE
        assert logs[0].model_type == Service.get_model_type()
        assert logs[0].target_id == response.json().get("id")

    @pytest.mark.asyncio
    async def test_update_not_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            test_tariff: Tariff,
    ) -> None:
        """Test service update service not found"""
        update_data = {
            "name": "Updated Test Service",
            "fee_type": FeeTypeEnum.CONSULAR,
            "tariff_services": [
                {
                    "price": 2,
                    "tax": 3,
                    "tariff_id": test_tariff.id,
                }

            ]
        }
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.put(
            url=app.url_path_for("admin:service-update", service_id=1000),
            json=update_data,
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Service not found"
