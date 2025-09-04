from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models import Service


class Urgency(Base):
    __tablename__ = "urgencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    # Relations
    services: Mapped[list["Service"]] = relationship(back_populates="urgency", foreign_keys="Service.urgency_id")

    def __repr__(self):  # pragma: no cover
        return f"<Urgency {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "urgency"
