from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin, ArchivedAtMixin


if TYPE_CHECKING:
    from app.models import Country, Urgency, VisaDuration, VisaType


class Service(ArchivedAtMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "services"

    FEE_TYPE_CONSULAR = "consular"
    FEE_TYPE_GENERAL = "general"

    FEE_TYPE_CHOICES = (
        (FEE_TYPE_CONSULAR, "Consular"),
        (FEE_TYPE_GENERAL, "General"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    fee_type: Mapped[str] = mapped_column(ChoiceType(FEE_TYPE_CHOICES))
    country_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=True
    )
    urgency_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("urgencies.id", ondelete="CASCADE"), nullable=True
    )
    visa_duration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("visa_durations.id", ondelete="CASCADE"), nullable=True
    )
    visa_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("visa_types.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    country: Mapped["Country"] = relationship(back_populates="services")
    urgency: Mapped["Urgency"] = relationship(back_populates="services")
    visa_duration: Mapped["VisaDuration"] = relationship(back_populates="services")
    visa_type: Mapped["VisaType"] = relationship(back_populates="services")

    def __repr__(self):  # pragma: no cover
        return f"<Service {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "service"
