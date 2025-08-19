import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User


pytestmark = pytest.mark.asyncio


class TestUsers:
    async def test_user_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User
    ):
        response = await async_client.get(
            app.url_path_for("admin:user-list"),
        )
        assert response.status_code == status.HTTP_200_OK
        results: list = response.json()
        assert len(results) == 1
        r_user = results[0]
        assert r_user["id"] == test_user.id
        assert r_user["email"] == test_user.email
        assert r_user["first_name"] == test_user.first_name
        assert r_user["last_name"] == test_user.last_name
        assert r_user["email_verified"] == test_user.email_verified
        assert r_user["is_active"] == test_user.is_active
        assert r_user["created_at"] == test_user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        assert r_user["updated_at"] == test_user.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    async def test_user_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User
    ):
        response = await async_client.get(
            app.url_path_for("admin:user-detail", user_id=test_user.id),
        )
        assert response.status_code == status.HTTP_200_OK
        result: dict = response.json()

        assert result["id"] == test_user.id
        assert result["email"] == test_user.email
        assert result["first_name"] == test_user.first_name
        assert result["last_name"] == test_user.last_name
        assert result["email_verified"] == test_user.email_verified
        assert result["is_active"] == test_user.is_active
        assert result["created_at"] == test_user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        assert result["updated_at"] == test_user.updated_at.strftime("%Y-%m-%d %H:%M:%S")
