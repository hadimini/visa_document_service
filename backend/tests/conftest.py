import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from pydantic.v1 import EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.api.server import get_application
from app.config import DATABASE_URL
from app.database.repositories.users import UsersRepository
from app.models.users import User
from app.schemas.user import UserCreateSchema


@pytest_asyncio.fixture
def app() -> FastAPI:
    return get_application()


async def handle_test_db(db_url: str):
    """Create database if it doesn't exist"""
    # Extract base URL without db name
    base_url = db_url.rsplit("/", 1)[0]
    db_name = db_url.split("/")[-1]

    # Connect to postgres default database to check/create our db
    temp_engine = create_async_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")

    async with temp_engine.connect() as conn:
        await conn.execute(
            text(f"DROP DATABASE IF EXISTS {db_name};")
        )
        await conn.execute(
            text(f"CREATE DATABASE {db_name} ENCODING 'utf8' TEMPLATE template1")
        )
        print(f"Created database {db_name}")

    await temp_engine.dispose()


from app.database.db import Base, get_session
@pytest_asyncio.fixture(scope="function")
async def async_db_engine():

    db_url = f"{DATABASE_URL}_test"

    await handle_test_db(db_url)

    async_engine = create_async_engine(
        url=db_url,
        echo=False,
        poolclass=NullPool,
    )

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


@pytest_asyncio.fixture
async def test_user(async_db: AsyncSession) -> User:
    new_user = UserCreateSchema(
        email=EmailStr("testuser@example.com"),
        first_name="James",
        last_name="Smith",
        password="samplepassword",
    )
    user_repo = UsersRepository(async_db)
    return await user_repo.create(new_user=new_user)
