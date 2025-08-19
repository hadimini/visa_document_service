import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.token import TokenPairSchema, JWTSchema
from app.services import jwt_service


pytestmark = pytest.mark.asyncio


class TestUsers:
    async def test_user_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User
    ):
        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=test_admin)
        access_token: JWTSchema = token_pair.access.token

        response = await async_client.get(
            app.url_path_for("admin:user-list"),
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        results: list = response.json()
        assert len(results) == 1
        r_user = results[0]
        assert r_user["id"] == test_admin.id
        assert r_user["email"] == test_admin.email
        assert r_user["first_name"] == test_admin.first_name
        assert r_user["last_name"] == test_admin.last_name
        assert r_user["email_verified"] == test_admin.email_verified
        assert r_user["is_active"] == test_admin.is_active
        assert r_user["role"] == test_admin.role
        assert r_user["created_at"] == test_admin.created_at.strftime(STRFTIME_FORMAT)
        assert r_user["updated_at"] == test_admin.updated_at.strftime(STRFTIME_FORMAT)

    async def test_user_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User
    ):
        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=test_admin)
        access_token: JWTSchema = token_pair.access.token

        response = await async_client.get(
            app.url_path_for("admin:user-detail", user_id=test_admin.id),
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        result: dict = response.json()

        assert result["id"] == test_admin.id
        assert result["email"] == test_admin.email
        assert result["first_name"] == test_admin.first_name
        assert result["last_name"] == test_admin.last_name
        assert result["email_verified"] == test_admin.email_verified
        assert result["is_active"] == test_admin.is_active
        assert result["created_at"] == test_admin.created_at.strftime(STRFTIME_FORMAT)
        assert result["updated_at"] == test_admin.updated_at.strftime(STRFTIME_FORMAT)
