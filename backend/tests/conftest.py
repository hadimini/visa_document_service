import os
import warnings

import alembic
import pytest_asyncio
from alembic.config import Config as AlembicConfig
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db import get_db


# Apply migrations at beginning and end of testing session
@pytest_asyncio.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = AlembicConfig("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest_asyncio.fixture
def app(apply_migrations) -> FastAPI:
    from app.api.server import get_application
    return get_application()



@pytest_asyncio.fixture
def db(app):
    return get_db()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            base_url="http://localhost:8000",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client


@pytest_asyncio.fixture
async def test_user(db: AsyncSession):
    pass
