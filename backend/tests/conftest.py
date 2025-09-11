import json
from pathlib import Path
from typing import Protocol, Optional

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
from app.database.db import get_session
from app.database.repositories.clients import ClientsRepository
from app.database.repositories.country_visas import CountryVisasRepository
from app.database.repositories.services import ServicesRepository
from app.database.repositories.tariffs import TariffsRepository
from app.database.repositories.urgencies import UrgenciesRepository
from app.database.repositories.users import UsersRepository
from app.database.repositories.visa_durations import VisaDurationsRepository
from app.database.repositories.visa_types import VisaTypesRepository
from app.models.base import Base
from app.models import (
    Applicant,
    Client,
    Country,
    CountryVisa,
    Order,
    Service,
    Tariff,
    Urgency,
    User,
    VisaType,
    VisaDuration,
)
from app.schemas.client import ClientCreateSchema, ClientTypeEnum
from app.schemas.country_visa import CountryVisaCreateSchema
from app.schemas.order.base import OrderStatusEnum
from app.schemas.service import ServiceCreateSchema, FeeTypeEnum, TariffServiceCreateSchema
from app.schemas.tariff import TariffCreateSchema
from app.schemas.urgency import UrgencyCreateSchema
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


@pytest_asyncio.fixture
async def client_maker(async_db: AsyncSession, test_tariff: Tariff):
    clients_repo = ClientsRepository(async_db)
    n = 1
    async def inner(*, name: Optional[str] = None, type: ClientTypeEnum):
        nonlocal n
        client = await clients_repo.create(
            new_client=ClientCreateSchema(
                name=name or f"Test Client {n}",
                type=type,
                tariff_id=test_tariff.id,
            )
        )
        n += 1
        return client
    return inner


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
        client_maker
) -> User:
    clients_repo = ClientsRepository(async_db)

    new_user = UserCreateSchema(
        email=EmailStr("individual@example.com"),
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


class VisaTypeMakerProtocol(Protocol):
    async def __call__(self, *, name: Optional[str] = None) -> VisaType:
        ...


@pytest_asyncio.fixture
async def visa_type_maker(async_db: AsyncSession) -> VisaTypeMakerProtocol:
    visa_types_repo = VisaTypesRepository(async_db)
    created_visa_types = []
    n = 1

    print("SETUP: Fixture initialization")
    # The fixture function runs up to the yield statement

    async def inner(*, name: str | None = None) -> VisaType:
        nonlocal n
        visa_type = await visa_types_repo.create(
            data=VisaTypeCreateSchema(
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


class UrgencyMakerProtocol(Protocol):
    async def __call__(self, *, name: Optional[str] = None) -> Urgency:
        ...


@pytest_asyncio.fixture
async def urgency_maker(async_db: AsyncSession):
    urgencies_repo = UrgenciesRepository(async_db)
    created_urgencies = []

    n = 1

    async def inner(*, name: str | None = None) -> Urgency:
        nonlocal n
        urgency = await urgencies_repo.create(
            data=UrgencyCreateSchema(
                name=name or f"Test Urgency {n}",
            )
        )
        created_urgencies.append(urgency)
        n += 1
        return urgency
    yield inner


class CountryMakerProtocol(Protocol):
    async def __call__(
            self,
            *,
            name: str,
            alpha2: str,
            alpha3: str,
            available_for_order: bool = False,
    ) -> Country:
        ...


@pytest_asyncio.fixture
async def country_maker(async_db: AsyncSession) -> CountryMakerProtocol:

    async def inner(*, name: str, alpha2: str, alpha3: str, available_for_order: bool = False) -> Country:
        country = Country(
            name=name,
            alpha2=alpha2,
            alpha3=alpha3,
            available_for_order=available_for_order,
        )
        async_db.add(country)
        await async_db.commit()
        return country

    return inner


class OrderMakerProtocol(Protocol):
    async def __call__(
            self,
            *,
            country: Country,
            client: Client,
            created_by: User,
            urgency: Urgency,
            visa_duration: VisaDuration,
            visa_type: VisaType,
            status: Optional[OrderStatusEnum] = None,
            applicant_data: Optional[dict[str, str]] = None,
    ) -> Order:
        ...


@pytest_asyncio.fixture
async def order_maker(async_db: AsyncSession) -> OrderMakerProtocol:

    async def inner(
            *,
            country: Country,
            client: Client,
            created_by: User,
            urgency: Urgency,
            visa_duration: VisaDuration,
            visa_type: VisaType,
            status: Optional[OrderStatusEnum] = None,
            applicant_data: Optional[dict[str, str]] = None,
    ) -> Order:
        order = Order(
            country_id=country.id,
            client_id=client.id,
            created_by_id=created_by.id,
            urgency_id=urgency.id,
            visa_duration_id=visa_duration.id,
            visa_type_id=visa_type.id,
            status=status,
        )
        async_db.add(order)
        await async_db.flush()

        if applicant_data:
            applicant = Applicant(
                first_name=applicant_data["first_name"],
                last_name=applicant_data["last_name"],
                gender=applicant_data["gender"],
                email=applicant_data["email"],
                order=order,
            )
            async_db.add(applicant)

        await async_db.commit()
        return order

    return inner


@pytest_asyncio.fixture()
async def country_visa_maker(async_db: AsyncSession):
    country_visas_repo = CountryVisasRepository(async_db)

    async def inner(*, country_id: int, visa_type_id: int, is_active: bool = True) -> CountryVisa:
        country_visa = await country_visas_repo.create(
            data=CountryVisaCreateSchema(
                country_id=country_id,
                visa_type_id=visa_type_id,
                is_active=is_active
            )
        )
        return country_visa
    return inner


class VisaDurationMakerProtocol(Protocol):
    async def __call__(self, *, term: str, entry: str) -> VisaDuration:
        ...


@pytest_asyncio.fixture
async def visa_duration_maker(async_db: AsyncSession):
    visa_durations_repo = VisaDurationsRepository(async_db)

    async def inner(*, term: str, entry: str) -> VisaDuration:
        visa_duration = await visa_durations_repo.create(term=term, entry=entry)
        return visa_duration
    return inner


@pytest_asyncio.fixture
async def service_maker(async_db: AsyncSession):
    services_repo = ServicesRepository(async_db)
    n = 1

    async def inner(
            *,
            fee_type: FeeTypeEnum,
            name: Optional[str] = None,
            tariff_services: Optional[list[TariffServiceCreateSchema]] = None
    ) -> Service:
        nonlocal n
        service = await services_repo.create(
            data=ServiceCreateSchema(
                name=name or f"Test Service {n}",
                fee_type=fee_type,
                tariff_services=tariff_services,
            )
        )
        n += 1
        return service
    return inner
