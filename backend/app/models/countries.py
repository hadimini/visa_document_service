from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


if TYPE_CHECKING:
    from app.models.country_visas import CountryVisa


class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    alpha2: Mapped[str] = mapped_column(String)
    alpha3: Mapped[str] = mapped_column(String)
    available_for_order: Mapped[bool] = mapped_column(Boolean, default=False)

    country_visas: Mapped[list["CountryVisa"]] = relationship(
        back_populates="country",
        foreign_keys="CountryVisa.country_id",
    )

    def __repr__(self):
        return f"<Country {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country"
