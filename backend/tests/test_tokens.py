import pytest
from fastapi import FastAPI

from app.models.users import User
from app.schemas.token import JWTSchema, TokenPairScheme
from app.services import jwt_service

pytestmark = pytest.mark.asyncio


class TestJwtToken:

    async def test_create_token_pair_success(
            self,
            app: FastAPI,
            test_user: User,
    ):
        token_pair: TokenPair = jwt_service.create_token_pair(user=test_user)

        access_token: JWTSchema = token_pair.access
        assert access_token.payload.sub == str(test_user.id)

        refresh_token: JWTSchema = token_pair.refresh
        assert refresh_token.payload.sub == str(test_user.id)

    async def test_token_missing_user_is_none(self, app: FastAPI) -> None:
        token_pair: TokenPair = jwt_service.create_token_pair(user=None)
        assert token_pair is None
