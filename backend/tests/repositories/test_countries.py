import pytest
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.countries import CountriesRepository
from app.models import Country
from app.schemas.country import CountryFilterSchema
from app.schemas.pagination import PageParamsSchema, PagedResponseSchema
from tests.conftest import async_db, CountryMakerProtocol


class TestCountriesRepository:
    """Tests for the CountriesRepository class."""

    @pytest.fixture
    def countries_repo(self, async_db: AsyncSession) -> CountriesRepository:
        return CountriesRepository(async_db)

    @pytest.mark.asyncio
    async def test_initialization(self, async_db: AsyncSession, countries_repo: CountriesRepository) -> None:
        assert countries_repo.db == async_db
        assert countries_repo.model == Country

    @pytest.mark.parametrize(
        "filter_data, expected_filter_count",
        (
            ({}, 0),
            ({"name": "russia"}, 1),
            ({"available_for_order": False}, 1),
            ({"name": "Russia", "available_for_order": True}, 2),
        )
    )
    def test_build_filters(
            self,
            countries_repo: CountriesRepository,
            load_countries,
            filter_data: dict,
            expected_filter_count
    ) -> None:
        """Test build filters method."""
        filter_schema = CountryFilterSchema(**filter_data)
        filters = countries_repo.build_filters(query_filters=filter_schema)

        assert len(filters) == expected_filter_count

    @pytest.mark.asyncio
    async def test_paginated_list(self, async_db: AsyncSession, countries_repo: CountriesRepository, load_countries) -> None:
        paginated_result = await countries_repo.get_paginated_list(
            query_filters=None,
            page_params=PageParamsSchema(
                page=1,
                size=1
            )
        )
        countries = (await async_db.scalars(select(Country).order_by(Country.id))).all()

        assert paginated_result == {
            **PagedResponseSchema(
                page=1,
                size=1,
                total=len(countries),
                total_pages=len(countries),
                has_next=True,
                has_prev=False,
            ).model_dump(),
            "items": [
                countries[0]
            ]
        }

    @pytest.mark.asyncio
    async def test_paginated_list_with_filters(self, async_db: AsyncSession, countries_repo: CountriesRepository, load_countries) -> None:
        paginated_result = await countries_repo.get_paginated_list(
            query_filters=CountryFilterSchema(
                name="Germany",
                available_for_order=False,
            ),
            page_params=PageParamsSchema(
                page=1,
                size=1
            )
        )
        germany = (
            await async_db.scalars(
                select(Country).where(
                    and_(Country.name == "Germany", Country.available_for_order == False)
                ).order_by(Country.id)
            )
        ).one_or_none()

        assert germany is not None
        assert paginated_result == {
            **PagedResponseSchema(
                page=1,
                size=1,
                total=1,
                total_pages=1,
                has_next=False,
                has_prev=False,
            ).model_dump(),
            "items": [
                germany
            ]
        }

    @pytest.mark.asyncio
    async def test_get_by_id(self, countries_repo: CountriesRepository, country_maker: CountryMakerProtocol):
        russia = await country_maker(name="Russia", alpha2="RU", alpha3="RUS", available_for_order=True)
        russia_in_db = await countries_repo.get_by_id(country_id=russia.id)

        assert russia_in_db is not None
        assert isinstance(russia_in_db, Country)
        assert russia_in_db.id == russia.id
        assert russia_in_db.name == russia.name
        assert russia_in_db.alpha2 == russia.alpha2
        assert russia_in_db.alpha3 == russia.alpha3

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, countries_repo: CountriesRepository):
        country = await countries_repo.get_by_id(country_id=1000)

        assert country is None
