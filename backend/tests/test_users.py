import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.token import JWTPayload
from app.services import auth_service, jwt_service

pytestmark = pytest.mark.asyncio


class TestGet:
    async def test_list(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User
    ):
        response = await async_client.get(
            app.url_path_for("users:user-list"),
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

    async def test_detail(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_user: User
    ):
        response = await async_client.get(
            app.url_path_for("users:user-detail", user_id=test_user.id),
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


class TestCreate:
    async def test_create_user_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
    ):
        user_rpo = UsersRepository(async_db)
        user_data = {
            "email": "user@example.com",
            "first_name": "James",
            "last_name": "Doe",
            "password": "samplepassword"
        }

        response = await async_client.post(
            app.url_path_for("users:user-create"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        user_in_db = await user_rpo.get_by_email(email=user_data["email"])
        assert user_in_db is not None
        assert user_in_db.first_name == user_data["first_name"]
        assert user_in_db.last_name == user_data["last_name"]

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
            app.url_path_for("users:user-create"),
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

    async def test_create_user_email_exists_error(
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
            app.url_path_for("users:user-create"),
            json=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:

    async def test_user_login_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_user: User,
    ):
        async_client.headers["content-type"] = "application/x-www-form-urlencoded"
        login_data = {
            "username": test_user.email,
            "password": "samplepassword",
        }
        response = await async_client.post(
            app.url_path_for("users:user-login"),
            data=login_data
        )
        assert response.status_code == status.HTTP_200_OK
        access_token = response.json().get("token")

        assert access_token is not None
        payload: JWTPayload = jwt_service.decode_token(token=access_token)
        assert payload.sub == str(test_user.id)
