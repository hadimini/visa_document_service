from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.m2m_country_visa_duration import country_visa_duration
from app.models.mixins import IsActiveMixin

if TYPE_CHECKING:
    from app.models import Country, VisaDuration, VisaType


class CountryVisa(IsActiveMixin, Base):
    __tablename__ = "country_visas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    visa_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("visa_types.id", ondelete="CASCADE"))

    country: Mapped["Country"] = relationship(back_populates="country_visas")
    visa_type: Mapped["VisaType"] = relationship(back_populates="country_visas")

    # Many-to-many relationship
    visa_durations: Mapped[list["VisaDuration"]] = relationship(
        secondary=country_visa_duration,
        back_populates="country_visas"
    )

    duration_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"<CountryVisa {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country_visa"
