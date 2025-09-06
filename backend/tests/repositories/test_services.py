import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.database.repositories.services import ServicesRepository
from app.models import Service
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from app.schemas.service import ServiceCreateSchema, ServiceFilterSchema, FeeTypeEnum

pytestmark = pytest.mark.asyncio


class TestServicesRepository:
    """Test class for ServicesRepository"""

    @pytest.fixture
    def services_repo(self, async_db: AsyncSession) -> ServicesRepository:
        return ServicesRepository(async_db)

    @pytest.fixture
    def audit_repo(self, async_db: AsyncSession) -> AuditRepository:
        return AuditRepository(async_db)

    @pytest.mark.asyncio
    async def test_initialization(self, async_db, services_repo):
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
    def test_build_filters(self, services_repo, filter_data, expected_filter_count):
        """Test build_filters method"""
        filter_schema = ServiceFilterSchema(**filter_data)
        filters = services_repo.build_filters(query_filters=filter_schema)
        assert len(filters) == expected_filter_count

    async def test_paginated_list(self, services_repo: ServicesRepository, service_maker):
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

    async def test_paginated_list_with_filters(self, services_repo: ServicesRepository, service_maker):
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
    async def test_get_by_id(self, services_repo: ServicesRepository, service_maker):
        """Test get_by_id when service exists"""
        service = await service_maker(fee_type=FeeTypeEnum.GENERAL)
        service_db = await services_repo.get_by_id(service_id=service.id)

        assert service.id == service_db.id
        assert service.fee_type == service_db.fee_type

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, services_repo: ServicesRepository):
        """Test get_by_id when service exists"""
        service = await services_repo.get_by_id(service_id=1000)

        assert service is None

    @pytest.mark.asyncio
    async def test_create_service(self, services_repo: ServicesRepository, audit_repo: AuditRepository):
        """Test service creation"""
        data = ServiceCreateSchema(name="Test Service", fee_type=FeeTypeEnum.GENERAL)
        service = await services_repo.create(data=data)

        assert service is not None
        assert service.name == "Test Service"
        assert service.fee_type == FeeTypeEnum.GENERAL
