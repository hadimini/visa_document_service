import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.urgencies import UrgenciesRepository
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
            test_admin: User,
            urgency_maker: UrgencyMakerProtocol,
    ) -> None:
        urgency = await urgency_maker(name="Express 3 days")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:urgency-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        print("\n\nresponse:", response.json())

    async def test_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            urgency_maker: UrgencyMakerProtocol,
    ) -> None:
        urgency = await urgency_maker(name="Express 3 days")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:urgency-detail", urgency_id=urgency.id),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == urgency.id
        assert response.json()["name"] == urgency.name

    async def test_detail_error_not_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:urgency-detail", urgency_id=1000),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Not found"

    async def test_create(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
    ) -> None:
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        urgencies_repo = UrgenciesRepository(async_db)
        response = await async_client.post(
            url=app.url_path_for("admin:urgency-create"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={
                "name": "Express 3 days",
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "Express 3 days"
        urgency_in_db = await urgencies_repo.get_by_id(urgency_id=response.json().get("id"))
        assert urgency_in_db.name == "Express 3 days"

    async def test_create_name_already_exists_error(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            urgency_maker: UrgencyMakerProtocol,
    ) -> None:
        await urgency_maker(name="Express 3 days")

        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.post(
            url=app.url_path_for("admin:urgency-create"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={
                "name": "Express 3 days",
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Name already exists"

    async def test_update(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            urgency_maker: UrgencyMakerProtocol
    ) -> None:
        urgency = await urgency_maker(name="Express 3 days")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.put(
            url=app.url_path_for("admin:urgency-update", urgency_id=urgency.id),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={"name": "New Name"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == urgency.id
        assert response.json()["name"] == "New Name" == urgency.name

    async def test_update_error_not_found(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User
    ) -> None:
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.put(
            url=app.url_path_for("admin:urgency-update", urgency_id=1000),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={"name": "New Name"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Not found"
