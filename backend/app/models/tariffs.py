from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.clients import Client


class Tariff(Base):
    __tablename__ = "tariffs"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    clients: Mapped[list["Client"]] = relationship(back_populates="tariff", foreign_keys="Client.tariff_id")

    def __repr__(self):  # pragma: no cover
        return "<Tariff {}>".format(self.id)

    @staticmethod
    def get_model_type() -> str:
        return "tariff"
