import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.visa_types import VisaTypesRepository
from app.models.users import User
from app.services import jwt_service
from tests.conftest import VisaTypeMakerProtocol

pytestmark = pytest.mark.asyncio


class TestVisaTypes:

    async def test_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            visa_type_maker
    ) -> None:
        visa_type = await visa_type_maker(name="Business")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:visa_type-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1
        response.json()["results"][0]["id"] = visa_type.id
        response.json()["results"][0]["name"] = visa_type.name

    async def test_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            visa_type_maker: VisaTypeMakerProtocol,
    ) -> None:
        visa_type = await visa_type_maker(name="Business")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:visa_type-detail", visa_type_id=visa_type.id),
            headers={"Authorization": f"Bearer {token_pair.access}"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == visa_type.id
        assert response.json()["name"] == visa_type.name

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
            url=app.url_path_for("admin:visa_type-detail", visa_type_id=1000),
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

        visa_types_repo = VisaTypesRepository(async_db)
        response = await async_client.post(
            url=app.url_path_for("admin:visa_type-create"),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={
                "name": "Business",
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "Business"
        visa_types_in_db = await visa_types_repo.get_by_id(visa_type_id=response.json().get("id"))
        assert visa_types_in_db.name == "Business"

    async def test_update(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            visa_type_maker: VisaTypeMakerProtocol
    ) -> None:
        visa_type = await visa_type_maker(name="Business")
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.put(
            url=app.url_path_for("admin:visa_type-update", visa_type_id=visa_type.id),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={"name": "New Name"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == visa_type.id
        assert response.json()["name"] == "New Name" == visa_type.name

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
            url=app.url_path_for("admin:visa_type-update", visa_type_id=1000),
            headers={"Authorization": f"Bearer {token_pair.access}"},
            json={"name": "New Name"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Not found"
