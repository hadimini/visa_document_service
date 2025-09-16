from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql.elements import ClauseElement

from app.database.repositories.base import BasePaginatedRepository
from app.database.repositories.mixins import BuildFiltersMixin
from app.database.repositories.users import UsersRepository
from app.models.clients import Client
from app.schemas.client import ClientCreateSchema, ClientFilterSchema
from app.schemas.pagination import PageParamsSchema


class ClientsRepository(BasePaginatedRepository[Client], BuildFiltersMixin):
    """Repository for managing client data in the database.

    This class provides methods to create, retrieve, and filter clients, as well as
    to handle pagination of client lists.

    Attributes:
        users_repo (UsersRepository): Repository for accessing user data.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the ClientsRepository with a database session.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        super().__init__(db=db, model=Client)
        self.users_repo = UsersRepository(db)

    def build_filters(self, *, query_filters: ClientFilterSchema) -> list:
        """Convert filter schema to SQLAlchemy filter conditions.

        This method constructs a list of filter conditions based on the provided
        ClientFilterSchema.

        Args:
            query_filters (ClientFilterSchema): The filter schema containing
                the attributes to filter by.

        Returns:
            list: A list of SQLAlchemy filter conditions.
        """
        filters: list[ClauseElement] = list()

        if query_filters.name:
            filters.append(Client.name.ilike(f"%{query_filters.name}%"))

        if query_filters.type:
            filters.append(Client.type == query_filters.type)
        return filters

    async def get_paginated_list(
            self,
            *,
            query_filters: Optional[ClientFilterSchema] = None,
            page_params: PageParamsSchema
    ) -> dict[str, Any]:
        """Retrieve a paginated list of clients based on filter criteria.

        This method fetches a list of clients with optional filtering and pagination.

        Args:
            query_filters (Optional[ClientFilterSchema]): The filters to apply to the client list.
            page_params (PageParamsSchema): The pagination parameters (page number and size).

        Returns:
            dict[str, Any]: A dictionary containing the paginated list of clients and metadata.
        """
        return await super().get_paginated_list(
            query_filters=query_filters,
            page_params=page_params,
            options=[selectinload(Client.tariff)]
        )

    async def get_by_id(self, *, client_id: int) -> Client | None:
        """Retrieve a client by their ID.

        This method fetches a client from the database based on the provided client ID.

        Args:
            client_id (int): The ID of the client to retrieve.

        Returns:
            Client | None: The retrieved client, or None if not found.
        """
        statement = select(Client).options(
            joinedload(Client.tariff)
        ).where(Client.id == client_id)
        result = await self.db.scalars(statement)
        return result.unique().one_or_none()

    async def create(self, *, new_client: ClientCreateSchema) -> Client:
        """Create a new client in the database.

        This method adds a new client based on the provided data schema and
        commits it to the database.

        Args:
            new_client (ClientCreateSchema): The data schema containing client details.

        Returns:
            Client: The created client instance.
        """
        data: dict = {
            "name": new_client.name,
            "tariff_id": new_client.tariff_id,
            "type": Client.TYPE_INDIVIDUAL,
            "email": new_client.email,
        }

        client = Client(**data)
        self.db.add(client)
        await self.db.commit()
        return client
