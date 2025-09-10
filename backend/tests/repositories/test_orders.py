import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.orders import OrdersRepository
from app.models import Order, VisaDuration, Applicant
from app.schemas.order.base import OrdersFilterSchema, OrderStatusEnum
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from tests.conftest import OrderMakerProtocol, CountryMakerProtocol


class TestOrdersRepository:
    """Tests for the Orders repository."""

    @pytest.fixture
    def orders_repo(self, async_db: AsyncSession) -> OrdersRepository:
        return OrdersRepository(async_db)

    @pytest.fixture
    @pytest.mark.asyncio
    async def russia(self, country_maker: CountryMakerProtocol):
        return await country_maker(name="Russia", alpha2="RU", alpha3="RUS")


    @pytest.mark.asyncio
    async def test_initialization(self, async_db: AsyncSession, orders_repo: OrdersRepository) -> None:
        """Test that the repository is initialized correctly"""
        assert orders_repo.db == async_db
        assert orders_repo.model == Order

    @pytest.mark.parametrize(
        "filter_data, expected_filter_count", [
            ({"status": "new"}, 1),
            ({"country_id": 1}, 1),
            ({"client_id": 1}, 1),
            ({"created_by_id": 1}, 1),
            ({"urgency_id": 1}, 1),
            ({"visa_duration_id": 1}, 1),
            ({"visa_type_id": 1}, 1),
            ({
                "status": "draft",
                "country_id": 1,
                "client_id": 2,
                "created_by_id": 3,
                "urgency_id": 4,
                "visa_duration_id": 5,
                "visa_type_id": 6,
            }, 7)
        ]
    )
    def test_build_filters(self, orders_repo: OrdersRepository, filter_data, expected_filter_count) -> None:
        """Test build_filters method"""
        filter_schema = OrdersFilterSchema(**filter_data)
        filters = orders_repo.build_filters(query_filters=filter_schema)

        assert len(filters) == expected_filter_count

    @pytest.mark.asyncio
    async def test_paginated_list(
            self,
            orders_repo: OrdersRepository,
            order_maker: OrderMakerProtocol,
            country_maker: CountryMakerProtocol,
            visa_duration_maker,
            visa_type_maker,
            test_individual,
            urgency_maker,
            test_user
    ) -> None:
        """Test that the paginated list is returned correctly"""
        country = await country_maker(name="Russia", alpha2="RU", alpha3="RUS")
        urgency = await urgency_maker()
        visa_duration = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)
        visa_type = await visa_type_maker(name="Business")
        client = await test_individual.awaitable_attrs.individual_client
        applicant_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "gender": Applicant.GENDER_MALE
        }

        orders = [
            await order_maker(
                country=country,
                client=client,
                created_by=test_user,
                urgency=urgency,
                visa_duration=visa_duration,
                visa_type=visa_type,
                status=OrderStatusEnum.DRAFT,
                applicant_data=applicant_data,
            )
            for _ in range(5)
        ]

        paginated_result = await orders_repo.get_paginated_list(
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
            "items": [orders[0]]
        }

    @pytest.mark.asyncio
    async def test_get_by_id(
            self,
            orders_repo: OrdersRepository,
            order_maker: OrderMakerProtocol,
            country_maker: CountryMakerProtocol,
            visa_duration_maker,
            visa_type_maker,
            test_individual,
            urgency_maker,
            test_user
    ) -> None:
        country = await country_maker(name="Russia", alpha2="RU", alpha3="RUS")
        urgency = await urgency_maker()
        visa_duration = await visa_duration_maker(term=VisaDuration.TERM_1, entry=VisaDuration.SINGLE_ENTRY)
        visa_type = await visa_type_maker(name="Business")
        client = await test_individual.awaitable_attrs.individual_client
        applicant_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "gender": Applicant.GENDER_MALE
        }
        order = await order_maker(
            country=country,
            client=client,
            created_by=test_user,
            urgency=urgency,
            visa_duration=visa_duration,
            visa_type=visa_type,
            status=OrderStatusEnum.NEW,
            applicant_data=applicant_data,
        )
        order_in_db = await orders_repo.get_by_id(order_id=order.id)

        assert order_in_db is not None
        assert isinstance(order_in_db, Order)
        assert order_in_db.id == order.id
        assert order_in_db.number == f"{order_in_db.created_at.year}-{order.id:04d}"
        assert order_in_db.status == Order.STATUS_NEW
        assert order_in_db.country == country
        assert order_in_db.client == client
        assert order_in_db.created_by == test_user
        assert order_in_db.urgency == urgency
        assert order_in_db.visa_duration == visa_duration
        assert order_in_db.visa_type == visa_type
        assert order_in_db.applicant.first_name == applicant_data["first_name"]
        assert order_in_db.applicant.last_name == applicant_data["last_name"]
        assert order_in_db.applicant.email == applicant_data["email"]
        assert order_in_db.applicant.gender == applicant_data["gender"]

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, orders_repo: OrdersRepository) -> None:
        order = await orders_repo.get_by_id(order_id=1000)

        assert order is None
