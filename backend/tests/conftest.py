import json
from pathlib import Path

import pytest_asyncio
from fastapi import FastAPI
from fastapi_mail import FastMail
from httpx import AsyncClient, ASGITransport
from pydantic.v1 import EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.api.server import get_application
from app.config import DATABASE_URL, mail_config

from app.database.repositories.clients import ClientRepository
from app.database.repositories.tariffs import TariffsRepository
from app.database.repositories.users import UsersRepository
from app.database.repositories.visa_types import VisaTypesRepository

from app.models.clients import Client
from app.models.countries import Country
from app.models.tariffs import Tariff
from app.models.users import User
from app.models.visa_types import VisaType
from app.schemas.client import ClientCreateSchema
from app.schemas.tariff import TariffCreateSchema
from app.schemas.user import UserCreateSchema
from app.schemas.visa_type import VisaTypeCreateSchema


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
async def fastapi_mail():
    mail_config.SUPPRESS_SEND = 1
    fm = FastMail(mail_config)
    return fm


@pytest_asyncio.fixture
async def test_tariff(
        async_db: AsyncSession,
) -> Tariff:
    new_tariff = TariffCreateSchema(
        name="Test Tariff",
        is_default=True
    )
    tariffs_repo = TariffsRepository(async_db)
    return await tariffs_repo.create(new_tariff=new_tariff)


# TODO: This may need update to create individual

@pytest_asyncio.fixture
async def test_user(async_db: AsyncSession) -> User:
    new_user = UserCreateSchema(
        email=EmailStr("testuser@example.com"),
        first_name="James",
        last_name="Smith",
        password="samplepassword",
    )
    users_repo = UsersRepository(async_db)
    return await users_repo.create(new_user=new_user)


@pytest_asyncio.fixture
async def test_admin(
        async_db: AsyncSession,
) -> User:
    new_user = UserCreateSchema(
        email=EmailStr("admin@example.com"),
        first_name="Max",
        last_name="Smith",
        password="Samplepassword",
        role=User.ROLE_ADMIN  # type: ignore[arg-type]
    )
    users_repo = UsersRepository(async_db)
    return await users_repo.create(new_user=new_user)


@pytest_asyncio.fixture
async def test_individual(
        async_db: AsyncSession,
        test_tariff: Tariff,
) -> User:
    clients_repo = ClientRepository(async_db)

    new_user = UserCreateSchema(
        email=EmailStr("admin@example.com"),
        first_name="Max",
        last_name="Smith",
        password="Samplepassword",
        role=User.ROLE_INDIVIDUAL  # type: ignore[arg-type]
    )
    client = await clients_repo.create(
        new_client=ClientCreateSchema(
            tariff_id=test_tariff.id,
            name=new_user.get_full_name(),
            type=Client.TYPE_INDIVIDUAL  # type: ignore[arg-type]
        )
    )
    new_user = new_user.model_copy(update={"individual_client_id": client.id})
    users_repo = UsersRepository(async_db)
    return await users_repo.create(new_user=new_user)


@pytest_asyncio.fixture(scope="function")
async def load_countries(async_db: AsyncSession) -> None:
    countries_json = Path(__file__).parent / "../fixtures/countries.json"

    with open(countries_json, "r") as f:
        data = json.load(f)

    for item in data:
        item.update({ "available_for_order": False })
        country = Country(**item)
        async_db.add(country)
    await async_db.commit()


@pytest_asyncio.fixture
async def visa_type_maker(async_db: AsyncSession):
    visa_types_repo = VisaTypesRepository(async_db)
    created_visa_types = []
    n = 1

    print("SETUP: Fixture initialization")
    # The fixture function runs up to the yield statement

    async def inner(*, name: str | None = None):
        nonlocal n
        visa_type = await visa_types_repo.create(
            visa_type=VisaTypeCreateSchema(
                name=name or f"Test Visa Type {n}",
            )
        )
        created_visa_types.append(visa_type)
        n += 1
        return visa_type

    yield inner

    print("TEARDOWN: Starting cleanup")
    # This runs AFTER the test completes
    # Consider cleanup
    # for visa_type in created_visa_types:
    #     await visa_types_repo.delete(visa_type.id)
