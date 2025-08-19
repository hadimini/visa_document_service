from collections.abc import Sequence

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.audit import AuditRepository
from app.database.repositories.users import UsersRepository
from app.models.audit import LogEntry
from app.models.users import User
from app.schemas.token import JWTPayloadSchema
from app.services import auth_service, jwt_service

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
    ):
        audit_repo = AuditRepository(async_db)

        user_rpo = UsersRepository(async_db)
        user_data = {
            "email": "user@example.com",
            "first_name": "James",
            "last_name": "Doe",
            "password": "samplepassword"
        }

        response = await async_client.post(
            app.url_path_for("auth:register"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        user_in_db = await user_rpo.get_by_email(email=user_data["email"])
        assert user_in_db is not None
        assert user_in_db.first_name == user_data["first_name"]
        assert user_in_db.last_name == user_data["last_name"]

        log_entries = await audit_repo.get_for_user(user_id=user_in_db.id)
        assert len(log_entries) == 1
        assert log_entries[0].user_id == user_in_db.id
        assert log_entries[0].action == LogEntry.ACTION_REGISTER

    async def test_saved_password_is_hashed_and_has_salt(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
    ):
        user_repo = UsersRepository(async_db)
        user_data = {
            "email": "test_user@example.io",
            "first_name": "James",
            "last_name": "Doe",
            "password": "Password"
        }

        response = await async_client.post(
            app.url_path_for("auth:register"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        db_user = await user_repo.get_by_email(email=user_data["email"])
        assert db_user is not None
        assert db_user.password is not None and db_user.password != user_data["password"]
        assert db_user.salt is not None
        assert auth_service.verify_password(
            password=user_data["password"],
            salt=db_user.salt,
            hashed_password=db_user.password,
        )

    async def test_register_email_exists_error(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_user: User,
    ) -> None:
        user_data = {
            "email": "testuser@example.com",
            "first_name": "Joe",
            "last_name": "Doe",
            "password": "PasswordSample"
        }
        response = await async_client.post(
            app.url_path_for("auth:register"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:

    async def test_user_login_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
    ):
        audit_repo = AuditRepository(async_db)
        log_entries: Sequence = await audit_repo.get_for_user(user_id=test_user.id)
        assert log_entries == []

        async_client.headers["content-type"] = "application/x-www-form-urlencoded"
        login_data = {
            "username": test_user.email,
            "password": "samplepassword",
        }
        response = await async_client.post(
            app.url_path_for("auth:login"),
            data=login_data
        )
        assert response.status_code == status.HTTP_200_OK
        access_token = response.json().get("token")
        # Check logs
        log_entries: Sequence | None = await audit_repo.get_for_user(user_id=test_user.id)
        assert len(log_entries) == 1
        log_entry = log_entries[0]
        assert log_entry.user_id == test_user.id
        assert log_entry.action == LogEntry.ACTION_LOGIN
        # Check tokens
        assert access_token is not None
        payload: JWTPayloadSchema = jwt_service.decode_token(token=access_token)
        assert payload.sub == str(test_user.id)
