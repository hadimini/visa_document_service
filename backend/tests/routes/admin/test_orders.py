import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.models import Client, Country, Order, Tariff, Urgency, User, VisaDuration, VisaType, LogEntry, Applicant
from app.schemas.applicant import ApplicantCreateUpdateSchema, ApplicantGenderEnum
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.order.admin import AdminOrderCreateSchema, AdminOrderUpdateSchema
from app.schemas.order.base import OrderStatusEnum
from app.services import jwt_service
from tests.conftest import (
    OrderMakerProtocol,
    CountryMakerProtocol,
    VisaDurationMakerProtocol,
    VisaTypeMakerProtocol,
    UrgencyMakerProtocol, visa_type_maker
)


class TestAdminOrdersRoutes:
    """Test class for the admin orders routes."""

    @pytest.fixture
    def audit_rpo(self, async_db: AsyncSession) -> AuditRepository:
        return AuditRepository(async_db)

    @pytest.fixture
    def access_token(self, test_admin):
        return jwt_service.create_token_pair(user=test_admin).access

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
            test_admin: User,
            access_token: str
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

        response = await async_client.get(
            url=app.url_path_for("admin:order-list"),
            headers={
                "Authorization": f"Bearer {access_token}"
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
            test_admin: User,
            access_token: str
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

        response = await async_client.get(
            url=app.url_path_for("admin:order-detail", order_id=order.id),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
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

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            access_token: str
    ) -> None:
        response = await async_client.get(
            url=app.url_path_for("admin:order-detail", order_id=1000),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Order not found"

    @pytest.mark.asyncio
    async def test_create_order(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            test_admin: User,
            country_maker: CountryMakerProtocol,
            urgency_maker: UrgencyMakerProtocol,
            visa_duration_maker: VisaDurationMakerProtocol,
            visa_type_maker: VisaTypeMakerProtocol,
            test_individual: User,
            access_token: str,
            audit_rpo
    ) -> None:
        country: Country = await country_maker(name="Russia", alpha2="RU", alpha3="RUS", available_for_order=True)
        urgency: Urgency = await urgency_maker()
        visa_duration: VisaDuration = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)
        visa_type: VisaType = await visa_type_maker(name="Tourist")
        data = AdminOrderCreateSchema(
            country_id=country.id,
            client_id=test_individual.individual_client_id,
            urgency_id=urgency.id,
            visa_duration_id=visa_duration.id,
            visa_type_id=visa_type.id,
        )

        response = await async_client.post(
            url=app.url_path_for("admin:order-create"),
            json=data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["MODEL_TYPE"] == Order.get_model_type()
        assert response.json()["status"] == OrderStatusEnum.DRAFT
        assert response.json()["number"] is not None
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
        assert response.json()["created_at"] is not None
        assert response.json()["updated_at"] is not None
        assert response.json()["completed_at"] is None
        assert response.json()["archived_at"] is None

        logs = await audit_rpo.get_for_user(user_id=test_admin.id)
        assert len(logs) == 1
        assert logs[0].user_id == test_admin.id
        assert logs[0].action == LogEntry.ACTION_CREATE
        assert logs[0].model_type == Order.get_model_type()
        assert logs[0].target_id == response.json().get("id")

    @pytest.mark.asyncio
    async def test_create_order_with_exception(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            access_token: str
    ) -> None:
        data = AdminOrderCreateSchema(
            country_id=1000,
            client_id=1000,
            urgency_id=1000,
            visa_duration_id=1000,
            visa_type_id=1000,
        )
        response = await async_client.post(
            url=app.url_path_for("admin:order-create"),
            json=data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Failed to create order"

    @pytest.mark.asyncio
    async def test_update_order(
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
            test_admin: User,
            access_token: str,
            audit_rpo
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

        country_2 = await country_maker(name="Germany", alpha2="DE", alpha3="DEU", available_for_order=True)
        urgency_2 = await urgency_maker()
        visa_duration_2 = await visa_duration_maker(term=VisaDuration.TERM_6, entry=VisaDuration.MULTIPLE_ENTRY)
        visa_type_2 = await visa_type_maker(name="Tourist")

        update_data = AdminOrderUpdateSchema(
            status=OrderStatusEnum.NEW,
            country_id=country_2.id,
            urgency_id=urgency_2.id,
            visa_duration_id=visa_duration_2.id,
            visa_type_id=visa_type_2.id,
            client_id=test_individual.individual_client_id,
            applicant=ApplicantCreateUpdateSchema(
                first_name="Joe",
                last_name="Smith",
                email="smith@example.com",
                gender=ApplicantGenderEnum.MALE
            )
        )

        response = await async_client.put(
            url=app.url_path_for("admin:order-update", order_id=order.id),
            json=update_data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == order.id
        assert response.json()["MODEL_TYPE"] == Order.get_model_type()
        assert response.json()["status"] == OrderStatusEnum.NEW
        assert response.json()["number"] == order.number
        assert response.json()["country"]["MODEL_TYPE"] == Country.get_model_type()
        assert response.json()["country"]["id"] == country_2.id
        assert response.json()["country"]["alpha2"] == country_2.alpha2
        assert response.json()["country"]["alpha3"] == country_2.alpha3
        assert response.json()["country"]["available_for_order"] is True

        assert response.json()["created_by"]["MODEL_TYPE"] == User.get_model_type()
        assert response.json()["created_by"]["id"] == test_admin.id
        assert response.json()["created_by"]["email"] == test_admin.email
        assert response.json()["created_by"]["first_name"] == test_admin.first_name
        assert response.json()["created_by"]["last_name"] == test_admin.last_name

        assert response.json()["urgency"]["MODEL_TYPE"] == Urgency.get_model_type()
        assert response.json()["urgency"]["id"] == urgency_2.id
        assert response.json()["urgency"]["name"] == urgency_2.name

        assert response.json()["visa_duration"]["MODEL_TYPE"] == VisaDuration.get_model_type()
        assert response.json()["visa_duration"]["id"] == visa_duration_2.id
        assert response.json()["visa_duration"]["name"] == visa_duration_2.name
        assert response.json()["visa_duration"]["term"] == visa_duration_2.term
        assert response.json()["visa_duration"]["entry"] == visa_duration_2.entry

        assert response.json()["visa_type"]["MODEL_TYPE"] == VisaType.get_model_type()
        assert response.json()["visa_type"]["id"] == visa_type_2.id
        assert response.json()["visa_type"]["name"] == visa_type_2.name

        client: Client = await test_individual.awaitable_attrs.individual_client
        assert response.json()["client"]["MODEL_TYPE"] == Client.get_model_type()
        assert response.json()["client"]["id"] == test_individual.individual_client_id
        assert response.json()["client"]["name"] == client.name
        assert response.json()["client"]["type"] == client.type

        tariff: Tariff = await client.awaitable_attrs.tariff
        assert response.json()["client"]["tariff"]["MODEL_TYPE"] == Tariff.get_model_type()
        assert response.json()["client"]["tariff"]["id"] == tariff.id
        assert response.json()["client"]["tariff"]["is_default"] == tariff.is_default

        assert response.json()["applicant"]["MODEL_TYPE"] == Applicant.get_model_type()
        assert response.json()["applicant"]["first_name"] == update_data.applicant.first_name
        assert response.json()["applicant"]["last_name"] == update_data.applicant.last_name
        assert response.json()["applicant"]["email"] == update_data.applicant.email
        assert response.json()["applicant"]["gender"] == update_data.applicant.gender

        assert response.json()["created_at"] == order.created_at.strftime(STRFTIME_FORMAT)
        assert response.json()["updated_at"] == order.updated_at.strftime(STRFTIME_FORMAT)
        assert response.json()["completed_at"] is None
        assert response.json()["archived_at"] is None

        logs = await audit_rpo.get_for_user(user_id=test_admin.id)
        assert len(logs) == 1
        assert logs[0].user_id == test_admin.id
        assert logs[0].action == LogEntry.ACTION_UPDATE
        assert logs[0].model_type == Order.get_model_type()
        assert logs[0].target_id == response.json().get("id")

        # Update applicant data again

        update_data = AdminOrderUpdateSchema(
            **update_data.model_dump(exclude={"applicant"}),
            applicant=ApplicantCreateUpdateSchema(
                first_name="Sue",
                last_name="Doe",
                email="sue@example.com",
                gender=ApplicantGenderEnum.FEMALE
            )
        )

        response = await async_client.put(
            url=app.url_path_for("admin:order-update", order_id=order.id),
            json=update_data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == order.id
        assert response.json()["MODEL_TYPE"] == Order.get_model_type()
        assert response.json()["status"] == OrderStatusEnum.NEW
        assert response.json()["number"] == order.number
        assert response.json()["country"]["MODEL_TYPE"] == Country.get_model_type()
        assert response.json()["country"]["id"] == country_2.id
        assert response.json()["country"]["alpha2"] == country_2.alpha2
        assert response.json()["country"]["alpha3"] == country_2.alpha3
        assert response.json()["country"]["available_for_order"] is True

        assert response.json()["created_by"]["MODEL_TYPE"] == User.get_model_type()
        assert response.json()["created_by"]["id"] == test_admin.id
        assert response.json()["created_by"]["email"] == test_admin.email
        assert response.json()["created_by"]["first_name"] == test_admin.first_name
        assert response.json()["created_by"]["last_name"] == test_admin.last_name

        assert response.json()["urgency"]["MODEL_TYPE"] == Urgency.get_model_type()
        assert response.json()["urgency"]["id"] == urgency_2.id
        assert response.json()["urgency"]["name"] == urgency_2.name

        assert response.json()["visa_duration"]["MODEL_TYPE"] == VisaDuration.get_model_type()
        assert response.json()["visa_duration"]["id"] == visa_duration_2.id
        assert response.json()["visa_duration"]["name"] == visa_duration_2.name
        assert response.json()["visa_duration"]["term"] == visa_duration_2.term
        assert response.json()["visa_duration"]["entry"] == visa_duration_2.entry

        assert response.json()["visa_type"]["MODEL_TYPE"] == VisaType.get_model_type()
        assert response.json()["visa_type"]["id"] == visa_type_2.id
        assert response.json()["visa_type"]["name"] == visa_type_2.name

        client: Client = await test_individual.awaitable_attrs.individual_client
        assert response.json()["client"]["MODEL_TYPE"] == Client.get_model_type()
        assert response.json()["client"]["id"] == test_individual.individual_client_id
        assert response.json()["client"]["name"] == client.name
        assert response.json()["client"]["type"] == client.type

        tariff: Tariff = await client.awaitable_attrs.tariff
        assert response.json()["client"]["tariff"]["MODEL_TYPE"] == Tariff.get_model_type()
        assert response.json()["client"]["tariff"]["id"] == tariff.id
        assert response.json()["client"]["tariff"]["is_default"] == tariff.is_default

        assert response.json()["applicant"]["MODEL_TYPE"] == Applicant.get_model_type()
        assert response.json()["applicant"]["first_name"] == update_data.applicant.first_name
        assert response.json()["applicant"]["last_name"] == update_data.applicant.last_name
        assert response.json()["applicant"]["email"] == update_data.applicant.email
        assert response.json()["applicant"]["gender"] == update_data.applicant.gender

        assert response.json()["created_at"] == order.created_at.strftime(STRFTIME_FORMAT)
        assert response.json()["updated_at"] == order.updated_at.strftime(STRFTIME_FORMAT)
        assert response.json()["completed_at"] is None
        assert response.json()["archived_at"] is None

        logs = await audit_rpo.get_for_user(user_id=test_admin.id)
        assert len(logs) == 2
        assert logs[-1].user_id == test_admin.id
        assert logs[-1].action == LogEntry.ACTION_UPDATE
        assert logs[-1].model_type == Order.get_model_type()
        assert logs[-1].target_id == response.json().get("id")

    @pytest.mark.asyncio
    async def test_update_order_not_found(
            self,
            app: FastAPI,
            async_db: AsyncSession,
            async_client: AsyncClient,
            access_token: str
    ) -> None:
        update_data = AdminOrderUpdateSchema(
            status=OrderStatusEnum.NEW,
            country_id=1,
            urgency_id=2,
            visa_duration_id=3,
            visa_type_id=4,
            client_id=5,
            applicant=None
        )

        response = await async_client.put(
            url=app.url_path_for("admin:order-update", order_id=1000),
            json=update_data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_order_with_exception(
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
            test_admin: User,
            access_token: str
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
        update_data = AdminOrderUpdateSchema(
            status=OrderStatusEnum.NEW,
            country_id=1,
            urgency_id=2,
            visa_duration_id=3,
            visa_type_id=4,
            client_id=5,
            applicant=None
        )

        response = await async_client.put(
            url=app.url_path_for("admin:order-update", order_id=order.id),
            json=update_data.model_dump(),
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Failed to update order"
