from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import IDIntMixin

if TYPE_CHECKING:
    from app.models import Client, TariffService


class Tariff(IDIntMixin, Base):
    __tablename__ = "tariffs"

    name: Mapped[str] = mapped_column(String(100))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    clients: Mapped[list["Client"]] = relationship(back_populates="tariff", foreign_keys="Client.tariff_id")
    tariff_services: Mapped[list["TariffService"]] = relationship(
        back_populates="tariff",
        foreign_keys="TariffService.tariff_id"
    )

    def __repr__(self):  # pragma: no cover
        return "<Tariff {}>".format(self.id)

    @staticmethod
    def get_model_type() -> str:
        return "tariff"
