from collections.abc import Sequence

import pytest
import requests_mock
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import MAILGUN_API_URL
from app.database.repositories.audit import AuditRepository
from app.database.repositories.clients import ClientRepository
from app.database.repositories.tokens import TokensRepository
from app.database.repositories.users import UsersRepository
from app.models import Tariff
from app.models.audit import LogEntry
from app.models.users import User
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.token import JWTPayloadSchema, TokenPairSchema, JWTSchema
from app.services import auth_service, jwt_service

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_tariff: Tariff,
    ):
        audit_repo = AuditRepository(async_db)
        clients_repo = ClientRepository(async_db)
        users_rpo = UsersRepository(async_db)
        user_data = {
            "email": "user@example.com",
            "first_name": "James",
            "last_name": "Doe",
            "password": "samplepassword"
        }
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                method="GET",
                url=MAILGUN_API_URL,
                status_code=200,
            )
            response = await async_client.post(
                app.url_path_for("auth:register"),
                json=user_data,
            )
            assert response.status_code == status.HTTP_201_CREATED

            user_in_db = await users_rpo.get_by_email(email=user_data["email"])
            assert user_in_db is not None
            assert user_in_db.first_name == user_data["first_name"]
            assert user_in_db.last_name == user_data["last_name"]
            assert user_in_db.role == User.ROLE_INDIVIDUAL
            assert user_in_db.individual_client_id is not None
            created_client = await clients_repo.get_by_id(client_id=user_in_db.individual_client_id)
            assert created_client.name == user_in_db.full_name

            log_entries = await audit_repo.get_for_user(user_id=user_in_db.id)
            assert len(log_entries) == 1
            assert log_entries[0].user_id == user_in_db.id
            assert log_entries[0].action == LogEntry.ACTION_REGISTER

    async def test_saved_password_is_hashed_and_has_salt(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_tariff: Tariff,
    ):
        users_repo = UsersRepository(async_db)
        user_data = {
            "email": "test_user@example.io",
            "first_name": "James",
            "last_name": "Doe",
            "password": "Password"
        }
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                method="GET",
                url=MAILGUN_API_URL,
                status_code=200,
            )
            response = await async_client.post(
                app.url_path_for("auth:register"),
                json=user_data,
            )
            assert response.status_code == status.HTTP_201_CREATED

            db_user = await users_repo.get_by_email(email=user_data["email"])
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
            test_tariff: Tariff,
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


class TestLogout:
    async def test_user_logout_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
    ):
        audit_repo = AuditRepository(async_db)
        log_entries = await audit_repo.get_for_user(user_id=test_user.id)
        assert log_entries == []

        tokens_repo = TokensRepository(async_db)
        blacklisted_tokens = await tokens_repo.get_all_blacklisted()
        assert blacklisted_tokens == []

        # Login

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

        # Logout

        response = await async_client.get(
            url=app.url_path_for("auth:logout"),
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"

        log_entries = await audit_repo.get_for_user(user_id=test_user.id)
        assert len(log_entries) == 2
        assert log_entries[0].user_id == test_user.id
        assert log_entries[0].action == LogEntry.ACTION_LOGOUT

        blacklisted_tokens = await tokens_repo.get_all_blacklisted()
        assert len(blacklisted_tokens) == 1
        access_token_jti = jwt_service.decode_token(token=access_token).jti
        assert str(blacklisted_tokens[0].id) == access_token_jti


class TestProfile:
    async def test_user_profile_detail_login_required(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_user: User,
    ):
        response = await async_client.get(
            app.url_path_for("auth:profile-detail")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_user_profile_update_login_required(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_user: User,
    ):
        update_data = {
            "first_name": "Updated fname",
            "last_name": "Updated lname",
        }
        response = await async_client.put(
            app.url_path_for("auth:profile-detail"),
            json=update_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_user_profile_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_user: User,
    ):
        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=test_user)
        access_token: JWTSchema = token_pair.access.token

        response = await async_client.get(
            app.url_path_for("auth:profile-detail"),
            headers={"Authorization": f"Bearer {access_token}"}

        )
        assert response.status_code == status.HTTP_200_OK
        user_data: dict = response.json()
        assert user_data["id"] == test_user.id
        assert user_data["email"] == test_user.email
        assert user_data["first_name"] == test_user.first_name
        assert user_data["last_name"] == test_user.last_name
        assert user_data["email_verified"] == test_user.email_verified
        assert user_data["is_active"] == test_user.is_active
        assert user_data["role"] == test_user.role
        assert user_data["created_at"] == test_user.created_at.strftime(STRFTIME_FORMAT)
        assert user_data["updated_at"] == test_user.updated_at.strftime(STRFTIME_FORMAT)

    async def test_user_profile_update(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User,
    ):
        audit_repo = AuditRepository(async_db)
        log_entries: Sequence = await audit_repo.get_for_user(user_id=test_user.id)
        assert log_entries == []

        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=test_user)
        access_token: JWTSchema = token_pair.access.token
        update_data = {
            "first_name": "Updated fname",
            "last_name": "Updated lname",
        }
        response = await async_client.put(
            app.url_path_for("auth:profile-detail"),
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        user_data: dict = response.json()
        assert user_data["id"] == test_user.id
        assert user_data["email"] == test_user.email
        assert user_data["first_name"] == update_data["first_name"]
        assert user_data["last_name"] == update_data["last_name"]
        assert user_data["email_verified"] == test_user.email_verified
        assert user_data["is_active"] == test_user.is_active
        assert user_data["role"] == test_user.role
        assert user_data["created_at"] == test_user.created_at.strftime(STRFTIME_FORMAT)
        assert user_data["updated_at"] == test_user.updated_at.strftime(STRFTIME_FORMAT)

        # Check logs

        log_entries: Sequence | None = await audit_repo.get_for_user(user_id=test_user.id)
        assert len(log_entries) == 1
        log_entry = log_entries[0]
        assert log_entry.user_id == test_user.id
        assert log_entry.action == LogEntry.ACTION_UPDATE
        assert log_entry.model_type == User.get_model_type()
        assert log_entry.target_id == test_user.id
