import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.services import jwt_service
from tests.conftest import UrgencyMakerProtocol

pytestmark = pytest.mark.asyncio


class TestUrgencies:

    async def test_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_individual: User,
            urgency_maker: UrgencyMakerProtocol,
    ) -> None:
        urgency = await urgency_maker(name="Express 3 days")
        token_pair = jwt_service.create_token_pair(user=test_individual)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("individual:urgency-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == urgency.id
        assert response.json()[0]["name"] == urgency.name
