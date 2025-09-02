import uuid
from datetime import datetime

import pytest
from fastapi import FastAPI, status
from freezegun import freeze_time
from httpx import AsyncClient

from app.models.users import User
from app.schemas.token import JWTPayloadSchema, JWTMetaSchema, JWTCredsSchema
from app.services import jwt_service

pytestmark = pytest.mark.asyncio


class TestJwtToken:

    async def test_create_token_pair_success(
            self,
            app: FastAPI,
            test_user: User,
    ):
        token_pair = jwt_service.create_token_pair(user=test_user)
        assert token_pair is not None

        access_token: str = token_pair.access
        decoded_token: JWTPayloadSchema = jwt_service.decode_token(token=access_token)
        assert decoded_token.type == jwt_service.TYPE_AUTH_TOKEN
        assert decoded_token.sub == str(test_user.id)
        assert decoded_token.role == test_user.role

        refresh_token: str = token_pair.refresh
        decoded_token: JWTPayloadSchema = jwt_service.decode_token(token=refresh_token)
        assert decoded_token.type == jwt_service.TYPE_AUTH_TOKEN
        assert decoded_token.sub == str(test_user.id)
        assert decoded_token.role == test_user.role

    async def test_token_missing_user_is_none(self, app: FastAPI) -> None:
        token_pair = jwt_service.create_token_pair(user=None)  # type: ignore[arg-type]
        assert token_pair is None

    async def test_token_expired(self, app: FastAPI, async_client: AsyncClient, test_user: User) -> None:
        with freeze_time("2020-01-01 10:00:00"):
            token_meta = JWTMetaSchema(
                jti=str(uuid.uuid4()),
                iat=int(datetime.now().timestamp())
            )
            token_creds = JWTCredsSchema(sub=str(test_user.id), type=jwt_service.TYPE_AUTH_TOKEN, role="admin")
            payload = JWTPayloadSchema(
                **token_meta.model_dump(),
                **token_creds.model_dump()
            )

            access_token = jwt_service.create_access_token(payload=payload, minutes=10)

        with freeze_time("2020-01-01 11:00:00"):

            response = await async_client.get(
                app.url_path_for("auth:profile-detail"),
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == "Expired token"
