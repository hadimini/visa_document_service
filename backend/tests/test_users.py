import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.get(app.url_path_for("users:user-list"))
        assert response.status_code == status.HTTP_200_OK
