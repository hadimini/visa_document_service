from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.services import ServicesRepository
from app.models import Service, Tariff, TariffService
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from app.schemas.service import (
    ServiceCreateSchema,
    ServiceFilterSchema,
    FeeTypeEnum,
    TariffServiceCreateSchema,
    ServiceUpdateSchema,
    TariffServiceUpdateSchema
)

pytestmark = pytest.mark.asyncio


class TestServicesRepository:
    """Test class for ServicesRepository"""

    @pytest.fixture
    def services_repo(self, async_db: AsyncSession) -> ServicesRepository:
        return ServicesRepository(async_db)

    @pytest.mark.asyncio
    async def test_initialization(self, async_db, services_repo) -> None:
        """Test that the repository is initialized correctly"""
        assert services_repo.model == Service
        assert services_repo.db == async_db

    @pytest.mark.parametrize(
        "filter_data,expected_filter_count", [
            ({}, 0),
            ({"name": "test"}, 1),
            ({"fee_type": "consular"}, 1),
            ({"country_id": 1}, 1),
            ({"urgency_id": 1}, 1),
            ({"visa_duration_id": 1}, 1),
            ({"visa_type_id": 1}, 1),
            ({
                 "name": "test",
                 "fee_type": "general",
                 "country_id": 1,
                 "urgency_id": 2,
                 "visa_duration_id": 3,
                 "visa_type_id": 4
             }, 6),
    ])
    def test_build_filters(self, services_repo, filter_data, expected_filter_count) -> None:
        """Test build_filters method"""
        filter_schema = ServiceFilterSchema(**filter_data)
        filters = services_repo.build_filters(query_filters=filter_schema)
        assert len(filters) == expected_filter_count

    async def test_paginated_list(self, services_repo: ServicesRepository, service_maker) -> None:
        """Test that the paginated list is returned correctly"""
        services = [
            await service_maker(fee_type=FeeTypeEnum.GENERAL)
            for _ in range(5)
        ]

        paginated_result = await services_repo.get_paginated_list(
            page_params=PageParamsSchema(
                page=1,
                size=1
            )
        )
        assert paginated_result == {
            **PagedResponseSchema(
            page=1,
            size=1,
            total=5,
            total_pages=5,
            has_next=True,
            has_prev=False,
        ).model_dump(),
            "items": [services[0]]
        }

    async def test_paginated_list_with_filters(self, services_repo: ServicesRepository, service_maker) -> None:
        """Test that the paginated list is returned correctly"""
        services = [
            await service_maker(fee_type=FeeTypeEnum.GENERAL)
            for _ in range(5)
        ]

        paginated_result = await services_repo.get_paginated_list(
            query_filters=ServiceFilterSchema(
                name="Test Service 1",
                fee_type=FeeTypeEnum.GENERAL,
            ),
            page_params=PageParamsSchema(
                page=1,
                size=10
            )
        )

        assert paginated_result == {
            **PagedResponseSchema(
            page=1,
            size=10,
            total=1,
            total_pages=1,
            has_next=False,
            has_prev=False,
        ).model_dump(),
            "items": [services[0]]
        }

    @pytest.mark.asyncio
    async def test_get_by_id(self, services_repo: ServicesRepository, service_maker) -> None:
        """Test get_by_id when service exists"""
        service = await service_maker(fee_type=FeeTypeEnum.GENERAL)
        service_db = await services_repo.get_by_id(service_id=service.id)

        assert service.id == service_db.id
        assert service.fee_type == service_db.fee_type

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, services_repo: ServicesRepository) -> None:
        """Test get_by_id when service does not exist"""
        service = await services_repo.get_by_id(service_id=1000)

        assert service is None

    @pytest.mark.asyncio
    async def test_create_service(self, services_repo: ServicesRepository) -> None:
        """Test service creation"""
        data = ServiceCreateSchema(name="Test Service", fee_type=FeeTypeEnum.GENERAL)
        service = await services_repo.create(data=data)

        assert service is not None
        assert service.name == "Test Service"
        assert service.fee_type == FeeTypeEnum.GENERAL

    @pytest.mark.asyncio
    async def test_create_service_with_tariffs(self, services_repo: ServicesRepository, test_tariff: Tariff) -> None:
        """Test service creation"""
        t_service = TariffServiceCreateSchema(
            price=Decimal(10.5),
            tax=Decimal(0.1),
            tariff_id=test_tariff.id
        )
        data = ServiceCreateSchema(
            name="Test Service",
            fee_type=FeeTypeEnum.GENERAL,
            tariff_services=[
                t_service,
            ]
        )
        service = await services_repo.create(data=data)

        ts_tax_amount = TariffService.calculate_tax(t_service.price, t_service.tax)
        ts_total = t_service.price + ts_tax_amount

        assert service is not None
        assert service.name == "Test Service"
        assert service.fee_type == FeeTypeEnum.GENERAL
        assert len(service.tariff_services) == 1
        assert service.tariff_services[0].price == t_service.price
        assert service.tariff_services[0].tax == t_service.tax
        assert service.tariff_services[0].tax_amount == ts_tax_amount
        assert service.tariff_services[0].total == ts_total
        assert service.tariff_services[0].service_id == service.id
        assert service.tariff_services[0].tariff_id == t_service.tariff_id

    @pytest.mark.asyncio
    async def test_update_service(self, services_repo: ServicesRepository, test_tariff: Tariff, service_maker) -> None:
        """Test service update"""
        t_service = TariffServiceCreateSchema(
            price=Decimal(10.5),
            tax=Decimal(0.1),
            tariff_id=test_tariff.id
        )
        service = await service_maker(fee_type=FeeTypeEnum.GENERAL, tariff_services=[t_service])
        new_t_service = TariffServiceUpdateSchema(
            price=Decimal(5.5),
            tax=Decimal(0.5),
            tariff_id=test_tariff.id
        )
        new_data = ServiceUpdateSchema(
            name="New name",
            fee_type=FeeTypeEnum.CONSULAR,
            tariff_services=[new_t_service]
        )
        await services_repo.update(service_id=service.id, data=new_data)

        new_ts_tax_amount = TariffService.calculate_tax(new_t_service.price, new_t_service.tax)
        new_ts_total = new_t_service.price + new_ts_tax_amount

        assert service is not None
        assert service.name == new_data.name
        assert service.fee_type == new_data.fee_type
        assert len(service.tariff_services) == 1
        assert service.tariff_services[0].price == new_t_service.price
        assert service.tariff_services[0].tax == new_t_service.tax
        assert service.tariff_services[0].tax_amount == new_ts_tax_amount
        assert service.tariff_services[0].total == new_ts_total
        assert service.tariff_services[0].service_id == service.id
        assert service.tariff_services[0].tariff_id == new_t_service.tariff_id

    @pytest.mark.asyncio
    async def test_update_service_not_found(self, services_repo: ServicesRepository, test_tariff) -> None:
        """Test service update"""

        new_t_service = TariffServiceUpdateSchema(
            price=Decimal(5.5),
            tax=Decimal(0.5),
            tariff_id=test_tariff.id
        )
        new_data = ServiceUpdateSchema(
            name="New name",
            fee_type=FeeTypeEnum.CONSULAR,
            tariff_services=[new_t_service]
        )
        service = await services_repo.update(service_id=1000, data=new_data)

        assert service is None
