from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import IDIntMixin

if TYPE_CHECKING:
    from app.models import CountryVisa, Service


class Country(IDIntMixin, Base):
    __tablename__ = 'countries'

    name: Mapped[str] = mapped_column(String)
    alpha2: Mapped[str] = mapped_column(String)
    alpha3: Mapped[str] = mapped_column(String)
    available_for_order: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    services: Mapped[list["Service"]] = relationship(
        back_populates="country",
        foreign_keys="Service.country_id",
    )

    country_visas: Mapped[list["CountryVisa"]] = relationship(
        back_populates="country",
        foreign_keys="CountryVisa.country_id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visa_data = None

    def __repr__(self):  # pragma: no cover
        return f"<Country {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country"
