import pytest
from fastapi import FastAPI

from app.models.users import User
from app.schemas.token import TokenPairSchema
from app.services import jwt_service

pytestmark = pytest.mark.asyncio


class TestJwtToken:

    async def test_create_token_pair_success(
            self,
            app: FastAPI,
            test_user: User,
    ):
        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=test_user)

        access_token: str = token_pair.access
        decoded_token: str = jwt_service.decode_token(token=access_token)
        assert decoded_token.type == jwt_service.TYPE_AUTH_TOKEN
        assert decoded_token.sub == str(test_user.id)
        assert decoded_token.role == test_user.role

        refresh_token: str = token_pair.refresh
        decoded_token: str = jwt_service.decode_token(token=refresh_token)
        assert decoded_token.type == jwt_service.TYPE_AUTH_TOKEN
        assert decoded_token.sub == str(test_user.id)
        assert decoded_token.role == test_user.role

    async def test_token_missing_user_is_none(self, app: FastAPI) -> None:
        token_pair: TokenPairSchema = jwt_service.create_token_pair(user=None)
        assert token_pair is None
