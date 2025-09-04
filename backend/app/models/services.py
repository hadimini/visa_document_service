from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin, ArchivedAtMixin


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
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    duration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("durations.id", ondelete="CASCADE"), nullable=True
    )
    visa_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("visa_types.id", ondelete="CASCADE"), nullable=True
    )
    urgency_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("urgencies.id", ondelete="CASCADE"), nullable=True
    )


    # TODO
    # visa_type, duration, urgency

    def __repr__(self):  # pragma: no cover
        return f"<Service {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "service"
