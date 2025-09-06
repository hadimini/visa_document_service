import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Client, User, Tariff
from app.services import jwt_service

pytestmark = pytest.mark.asyncio


class TestClients:
    async def test_list_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            async_db: AsyncSession,
            test_admin: User,
            test_individual
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:client-list"),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

        assert response.json()["items"][0]["MODEL_TYPE"] == Client.get_model_type()
        assert response.json()["items"][0]["id"] == test_individual.individual_client_id
        assert response.json()["items"][0]["name"] == test_individual.full_name
        assert response.json()["items"][0]["type"] == Client.TYPE_INDIVIDUAL
        assert response.json()["items"][0]["tariff"]["is_default"] is True
        client = await test_individual.awaitable_attrs.individual_client
        assert response.json()["items"][0]["tariff"]["MODEL_TYPE"] == Tariff.get_model_type()
        assert response.json()["items"][0]["tariff"]["id"] == client.tariff.id
        assert response.json()["items"][0]["tariff"]["name"] == client.tariff.name

    async def test_detail_success(
            self,
            app: FastAPI,
            async_client: AsyncClient,
            test_admin: User,
            test_individual
    ):
        token_pair = jwt_service.create_token_pair(user=test_admin)
        assert token_pair is not None

        response = await async_client.get(
            url=app.url_path_for("admin:client-detail", client_id=test_individual.individual_client_id),
            headers={"Authorization": f"Bearer {token_pair.access}"}
        )
        assert response.status_code == 200

        result: dict = response.json()
        assert result["MODEL_TYPE"] == Client.get_model_type()
        assert result["id"] == test_individual.individual_client_id
        assert result["name"] == test_individual.full_name
        assert result["type"] == Client.TYPE_INDIVIDUAL
        assert result["tariff"]["MODEL_TYPE"] == Tariff.get_model_type()
        assert result["tariff"]["is_default"] is True
        client: Client = await test_individual.awaitable_attrs.individual_client
        assert result["tariff"]["id"] == client.tariff.id
        assert result["tariff"]["name"] == client.tariff.name
