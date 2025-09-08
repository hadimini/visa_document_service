import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.clients import ClientsRepository
from app.models import Client
from app.schemas.client import ClientFilterSchema, ClientTypeEnum, ClientCreateSchema
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema


class TestClientsRepository:
    """Test class for ClientsRepository"""

    @pytest.fixture
    def clients_repo(self, async_db: AsyncSession) -> ClientsRepository:
        return ClientsRepository(async_db)

    @pytest.mark.asyncio
    async def test_initialization(self, async_db, clients_repo) -> None:
        """Test that the repository is initialized correctly"""
        assert clients_repo.db == async_db
        assert clients_repo.model == Client

    @pytest.mark.parametrize(
        "filter_data, expected_filter_count",[
            ({}, 0),
            ({"name": "Test client"}, 1),
            ({"type": "individual"}, 1),
            ({"name": "Test client", "type": "legal"}, 2),
        ]
    )
    def test_build_filters(self, clients_repo, filter_data, expected_filter_count) -> None:
        """Test that the filters are built correctly"""
        filter_schema = ClientFilterSchema(**filter_data)
        filters = clients_repo.build_filters(query_filters=filter_schema)

        assert len(filters) == expected_filter_count

    @pytest.mark.asyncio
    async def test_paginated_list(self, clients_repo, client_maker) -> None:
        """Test that the paginated list is built correctly"""
        clients = [
            await client_maker(type=ClientTypeEnum.LEGAL)
            for _ in range(5)
        ]
        paginated_result = await clients_repo.get_paginated_list(
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
            "items": [
                clients[0]
            ]
        }

    @pytest.mark.asyncio
    async def test_paginated_list_with_filters(self, clients_repo: ClientsRepository, client_maker) -> None:
        """Test that the paginated list is returned correctly"""
        clients = [
            await client_maker(type=ClientTypeEnum.INDIVIDUAL)
            for _ in range(5)
        ]
        paginated_result = await clients_repo.get_paginated_list(
            query_filters=ClientFilterSchema(
                name="Test Client 1",
                type=ClientTypeEnum.INDIVIDUAL,
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
            "items": [clients[0]]
        }

    @pytest.mark.asyncio
    async def test_get_by_id(self, clients_repo: ClientsRepository, client_maker) -> None:
        """Test get_by_id when client exists"""
        client = await client_maker(type=ClientTypeEnum.INDIVIDUAL)
        client_in_db = await clients_repo.get_by_id(client_id=client.id)

        assert client.id == client_in_db.id
        assert client.type == client_in_db.type

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, clients_repo: ClientsRepository) -> None:
        """Test get_by_id when client does not exist"""
        client = await clients_repo.get_by_id(client_id=1000)

        assert client is None

    @pytest.mark.asyncio
    async def test_create_client(self, test_tariff, clients_repo: ClientsRepository) -> None:
        """Test client creation"""
        data = ClientCreateSchema(name="Client ABC", type=ClientTypeEnum.INDIVIDUAL, tariff_id=test_tariff.id)
        client = await clients_repo.create(new_client=data)

        assert client is not None
        assert client.name == data.name
        assert client.type == ClientTypeEnum.INDIVIDUAL
        assert client.tariff_id == data.tariff_id
