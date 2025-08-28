from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import IsActiveMixin

if TYPE_CHECKING:
    from app.models.countries import Country
    from app.models.visa_types import VisaType


class CountryVisa(IsActiveMixin, Base):
    __tablename__ = "country_visas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    visa_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("visa_types.id", ondelete="CASCADE"))

    country: Mapped["Country"] = relationship(back_populates="country_visas")
    visa_type: Mapped["VisaType"] = relationship(back_populates="country_visas")

    def __repr__(self):
        return f"<CountryVisa {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country_visa"
