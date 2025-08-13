import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.api.server import get_application
from app.config import DATABASE_URL


@pytest_asyncio.fixture
def app() -> FastAPI:
    return get_application()

async_engine = create_async_engine(
    url=f"{DATABASE_URL}_test",
    echo=False,
    poolclass=NullPool,
)

from app.database.db import Base, get_session
@pytest_asyncio.fixture(scope="function")
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_db(async_db_engine):
    async_session = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_client(async_db, app: FastAPI):
    def override_get_db():
        yield async_db

    app.dependency_overrides[get_session] = override_get_db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

#
# @pytest_asyncio.fixture
# async def test_user(db: AsyncSession):
#     new_user = UserCreate(
#         email="user@example.com",
#         name="James",
#         password="samplepassword",
#     )
#     user_repo = UsersRepository(db)
#     return await user_repo.create(new_user=new_user)
