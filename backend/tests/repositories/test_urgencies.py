import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.urgencies import UrgenciesRepository
from app.exceptions import NameExistsException
from app.models import Urgency
from app.schemas.urgency import UrgencyCreateSchema, UrgencyUpdateSchema
from tests.conftest import UrgencyMakerProtocol


class TestUrgenciesRepository:
    """Test the Urgencies repository."""

    @pytest.fixture
    def urgencies_repo(self, async_db: AsyncSession) -> UrgenciesRepository:
        return UrgenciesRepository(async_db)

    @pytest.mark.asyncio
    async def test_initialization(self, async_db: AsyncSession, urgencies_repo: UrgenciesRepository) -> None:
        assert urgencies_repo.db == async_db

    @pytest.mark.asyncio
    async def test_list(self, urgencies_repo: UrgenciesRepository, urgency_maker: UrgencyMakerProtocol) -> None:
        urgencies = [
            await urgency_maker()
            for _ in range(10)
        ]

        urgencies_db = await urgencies_repo.get_list()
        assert len(urgencies_db) == 10

        for i, urgency in enumerate(urgencies_db):
            assert isinstance(urgency, Urgency)
            assert urgency.id == urgencies[i].id
            assert urgency.name == urgencies[i].name

    @pytest.mark.asyncio
    async def test_get_by_id(self, urgencies_repo: UrgenciesRepository, urgency_maker: UrgencyMakerProtocol) -> None:
        urgency = await urgency_maker()
        urgency_db = await urgencies_repo.get_by_id(urgency_id=urgency.id)

        assert isinstance(urgency_db, Urgency)
        assert urgency_db.id == urgency_db.id
        assert urgency_db.name == urgency.name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, urgencies_repo: UrgenciesRepository) -> None:
        urgency_db = await urgencies_repo.get_by_id(urgency_id=1000)

        assert urgency_db is None

    @pytest.mark.asyncio
    async def test_create_urgency(self, urgencies_repo: UrgenciesRepository) -> None:
        urgency = await urgencies_repo.create(data=UrgencyCreateSchema(name="Urgency name"))

        assert isinstance(urgency, Urgency)
        assert urgency.name == "Urgency name"

    @pytest.mark.asyncio
    async def test_create_urgency_name_exists(self, urgencies_repo: UrgenciesRepository, urgency_maker: UrgencyMakerProtocol) -> None:
        await urgency_maker(name="Urgency name")
        with pytest.raises(NameExistsException, match="Name already exists"):
            await urgencies_repo.create(data=UrgencyCreateSchema(name="Urgency name"))

    @pytest.mark.asyncio
    async def test_update_urgency(self, urgencies_repo: UrgenciesRepository, urgency_maker: UrgencyMakerProtocol) -> None:
        urgency = await urgency_maker()
        data = UrgencyUpdateSchema(name="New name")

        await urgencies_repo.update(urgency_id=urgency.id, data=data)
        assert isinstance(urgency, Urgency)
        assert urgency.name == data.name

    @pytest.mark.asyncio
    async def test_update_urgency_not_found(self, urgencies_repo: UrgenciesRepository) -> None:
        data = UrgencyUpdateSchema(name="New name")
        urgency = await urgencies_repo.update(urgency_id=1000, data=data)

        assert urgency is None
