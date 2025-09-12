import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.models import Client, Country, Order, Tariff, Urgency, User, VisaDuration, VisaType
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.order.base import OrderStatusEnum
from app.services import jwt_service
from tests.conftest import (
    OrderMakerProtocol,
    CountryMakerProtocol,
    VisaDurationMakerProtocol,
    VisaTypeMakerProtocol,
    UrgencyMakerProtocol
)


class TestAdminOrdersRoutes:
    """Test class for the admin orders routes."""

    @pytest.fixture
    def audit_rpo(self, async_db: AsyncSession) -> AuditRepository:
        return AuditRepository(async_db)

    @pytest.mark.asyncio
    async def test_list(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            order_maker: OrderMakerProtocol,
            country_maker: CountryMakerProtocol,
            visa_duration_maker: VisaDurationMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            test_individual: User,
            urgency_maker: UrgencyMakerProtocol,
            test_admin: User
    ) -> None:
        country = await country_maker(name="Russia", alpha2="RU", alpha3="RUS")
        urgency = await urgency_maker()
        visa_duration = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)
        visa_type = await visa_type_maker(name="Business")
        client = await test_individual.awaitable_attrs.individual_client

        for _ in range(2):
            await order_maker(
                country=country,
                client=client,
                created_by=test_admin,
                urgency=urgency,
                visa_duration=visa_duration,
                visa_type=visa_type,
                status=OrderStatusEnum.DRAFT
            )
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:order-list"),
            headers={
                "Authorization": f"Bearer {token_pair.access}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["page"] == 1
        assert response.json()["size"] == 25
        assert response.json()["total"] == 2
        assert response.json()["total_pages"] == 1
        assert response.json()["has_next"] is False
        assert response.json()["has_prev"] is False
        assert len(response.json()["items"]) == 2


    @pytest.mark.asyncio
    async def test_get_by_id(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            order_maker: OrderMakerProtocol,
            country_maker: CountryMakerProtocol,
            visa_duration_maker: VisaDurationMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            test_individual: User,
            urgency_maker: UrgencyMakerProtocol,
            test_admin: User
    ) -> None:
        country = await country_maker(name="Russia", alpha2="RU", alpha3="RUS", available_for_order=True)
        urgency = await urgency_maker()
        visa_duration = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)
        visa_type = await visa_type_maker(name="Business")
        client = await test_individual.awaitable_attrs.individual_client
        order = await order_maker(
                country=country,
                client=client,
                created_by=test_admin,
                urgency=urgency,
                visa_duration=visa_duration,
                visa_type=visa_type,
                status=OrderStatusEnum.DRAFT
            )
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:order-detail", order_id=order.id),
            headers={
                "Authorization": f"Bearer {token_pair.access}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        print("\n\n", response.json())
        assert response.json()["id"] == order.id
        assert response.json()["MODEL_TYPE"] == Order.get_model_type()
        assert response.json()["status"] == OrderStatusEnum.DRAFT
        assert response.json()["number"] == order.number
        assert response.json()["country"]["MODEL_TYPE"] == Country.get_model_type()
        assert response.json()["country"]["id"] == country.id
        assert response.json()["country"]["alpha2"] == country.alpha2
        assert response.json()["country"]["alpha3"] == country.alpha3
        assert response.json()["country"]["available_for_order"] is True

        assert response.json()["created_by"]["MODEL_TYPE"] == User.get_model_type()
        assert response.json()["created_by"]["id"] == test_admin.id
        assert response.json()["created_by"]["email"] == test_admin.email
        assert response.json()["created_by"]["first_name"] == test_admin.first_name
        assert response.json()["created_by"]["last_name"] == test_admin.last_name

        assert response.json()["urgency"]["MODEL_TYPE"] == Urgency.get_model_type()
        assert response.json()["urgency"]["id"] == urgency.id
        assert response.json()["urgency"]["name"] == urgency.name

        assert response.json()["visa_duration"]["MODEL_TYPE"] == VisaDuration.get_model_type()
        assert response.json()["visa_duration"]["id"] == visa_duration.id
        assert response.json()["visa_duration"]["name"] == visa_duration.name
        assert response.json()["visa_duration"]["term"] == visa_duration.term
        assert response.json()["visa_duration"]["entry"] == visa_duration.entry

        assert response.json()["visa_type"]["MODEL_TYPE"] == VisaType.get_model_type()
        assert response.json()["visa_type"]["id"] == visa_type.id
        assert response.json()["visa_type"]["name"] == visa_type.name

        client: Client = await test_individual.awaitable_attrs.individual_client
        assert response.json()["client"]["MODEL_TYPE"] == Client.get_model_type()
        assert response.json()["client"]["id"] == test_individual.individual_client_id
        assert response.json()["client"]["name"] == client.name
        assert response.json()["client"]["type"] == client.type

        tariff: Tariff = await client.awaitable_attrs.tariff
        assert response.json()["client"]["tariff"]["MODEL_TYPE"] == Tariff.get_model_type()
        assert response.json()["client"]["tariff"]["id"] == tariff.id
        assert response.json()["client"]["tariff"]["is_default"] == tariff.is_default

        assert response.json()["applicant"] is None
        assert response.json()["created_at"] == order.created_at.strftime(STRFTIME_FORMAT)
        assert response.json()["updated_at"] == order.updated_at.strftime(STRFTIME_FORMAT)
        assert response.json()["completed_at"] is None
        assert response.json()["archived_at"] is None
