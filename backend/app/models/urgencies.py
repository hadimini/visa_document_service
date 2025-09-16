from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import IDIntMixin

if TYPE_CHECKING:
    from app.models import Service


class Urgency(IDIntMixin, Base):
    __tablename__ = "urgencies"

    name: Mapped[str] = mapped_column(String)

    # Relations
    services: Mapped[list["Service"]] = relationship(back_populates="urgency", foreign_keys="Service.urgency_id")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Urgency {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "urgency"
