from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.m2m_country_visa_duration import country_visa_duration
from app.models.mixins import IDIntMixin, IsActiveMixin


if TYPE_CHECKING:
    from app.models import Country, VisaDuration, VisaType


class CountryVisa(IDIntMixin, IsActiveMixin, Base):
    __tablename__ = "country_visas"

    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    visa_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("visa_types.id", ondelete="CASCADE"))

    country: Mapped["Country"] = relationship(back_populates="country_visas")
    visa_type: Mapped["VisaType"] = relationship(back_populates="country_visas")

    # Many-to-many relationship
    visa_durations: Mapped[list["VisaDuration"]] = relationship(
        secondary=country_visa_duration,
        back_populates="country_visas"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.duration_data = None

    def __repr__(self):  # pragma: no cover
        return f"<CountryVisa {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country_visa"
