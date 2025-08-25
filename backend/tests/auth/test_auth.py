from collections.abc import Sequence
from urllib.parse import urljoin

import pytest
from fastapi import FastAPI, status
from fastapi_mail import FastMail
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import mail_config, BACKEND_URL
from app.database.repositories.audit import AuditRepository
from app.database.repositories.clients import ClientRepository
from app.database.repositories.tokens import TokensRepository
from app.database.repositories.users import UsersRepository
from app.helpers import fetch_urls_from_text, fetch_url_param_value
from app.models import Tariff
from app.models.audit import LogEntry
from app.models.users import User
from app.schemas.core import STRFTIME_FORMAT
from app.schemas.token import JWTPayloadSchema
from app.services import auth_service, jwt_service

pytestmark = pytest.mark.asyncio


class TestRegister:

    async def test_register_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            fastapi_mail: FastMail,
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

        with fastapi_mail.record_messages() as outbox:
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

            # Email
            assert len(outbox) == 1
            captured_email = outbox[0]
            assert captured_email["from"] == mail_config.MAIL_FROM
            assert captured_email["to"] == user_in_db.email
            assert captured_email["subject"] == "Action Required: Verify Your Email"
            assert captured_email.is_multipart() is True

            for part in captured_email.walk():
                ctype = part.get_content_type()
                cdisp = part.get("Content-Disposition")

                if ctype == "multipart/mixed" and not cdisp:
                    body = part.get_payload()[0].get_payload(decode=True).decode("utf-8")
                    assert "Please confirm your email address by clicking the link below" in body
                    urls = fetch_urls_from_text(body)
                    token = fetch_url_param_value(url=urls[0], param="token")
                    confirm_url = urljoin(BACKEND_URL, "auth/confirm-email?token=" + token)
                    assert confirm_url in body
                    break


    async def test_saved_password_is_hashed_and_has_salt(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            fastapi_mail: FastMail,
            test_tariff: Tariff,
    ):
        users_repo = UsersRepository(async_db)
        user_data = {
            "email": "test_user@example.io",
            "first_name": "James",
            "last_name": "Doe",
            "password": "Password"
        }
        with fastapi_mail.record_messages() as outbox:
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

    @pytest.mark.parametrize(
        "email, first_name, last_name, password, status_code",
        [
            ("", "James", "Doe", "password", 422),
            ("james_doe@exmaple.com", "", "Doe", "password", 422),
            ("james_doe@exmaple.com", "James", "", "password", 422),
            ("james_doe@exmaple.com", "James", "Doe", "", 422),
        ]
    )
    async def test_registration_error(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            fastapi_mail: FastMail,
            test_tariff: Tariff,
            email: str,
            first_name: str,
            last_name: str,
            password: str,
            status_code: int,
    ):
        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password
        }

        response = await async_client.post(
            app.url_path_for("auth:register"),
            json=user_data,
        )
        assert response.status_code == status_code

    async def test_email_confirm_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            fastapi_mail: FastMail,
            test_tariff: Tariff
    ):
        token = None
        audit_repo = AuditRepository(async_db)
        clients_repo = ClientRepository(async_db)
        users_rpo = UsersRepository(async_db)
        user_data = {
            "email": "user1@example.com",
            "first_name": "James",
            "last_name": "Doe",
            "password": "samplepassword"
        }

        with fastapi_mail.record_messages() as outbox:
            await async_client.post(
                app.url_path_for("auth:register"),
                json=user_data,
            )
            user_in_db = await users_rpo.get_by_email(email=user_data["email"])
            assert user_in_db is not None
            assert user_in_db.individual_client_id is not None

            # Email
            assert len(outbox) == 1
            captured_email = outbox[0]
            assert captured_email["from"] == mail_config.MAIL_FROM
            assert captured_email["to"] == user_in_db.email
            assert captured_email["subject"] == "Action Required: Verify Your Email"
            assert captured_email.is_multipart() is True

            for part in captured_email.walk():
                ctype = part.get_content_type()
                cdisp = part.get("Content-Disposition")

                if ctype == "multipart/mixed" and not cdisp:
                    body = part.get_payload()[0].get_payload(decode=True).decode("utf-8")
                    assert "Please confirm your email address by clicking the link below" in body
                    urls = fetch_urls_from_text(body)
                    token = fetch_url_param_value(url=urls[0], param="token")
                    break
        assert token is not None
        confirm_url = urljoin(BACKEND_URL, "auth/confirm-email?token=" + token)
        response = await async_client.get(confirm_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("message") == "Email successfully confirmed"

        log_entries = await audit_repo.get_for_user(user_id=user_in_db.id)
        assert len(log_entries) == 2
        assert log_entries[0].user_id == user_in_db.id
        assert log_entries[0].action == LogEntry.ACTION_VERIFY

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

    @pytest.mark.parametrize(
        "email, password, status_code",
        [
            ("", "password", 401),
            ("user@example.com", "", 401),
            ("notfound@example.com", "password", 401),
        ]
    )
    async def test_user_login_error(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            email: str,
            password: str,
            status_code: int,
    ):
        async_client.headers["content-type"] = "application/x-www-form-urlencoded"
        login_data = {
            "username": email,
            "password": password,
        }
        response = await async_client.post(
            app.url_path_for("auth:login"),
            data=login_data
        )
        assert response.status_code == status_code


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
        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None

        access_token: str = token_pair.access
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

        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None

        access_token: str = token_pair.access
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
