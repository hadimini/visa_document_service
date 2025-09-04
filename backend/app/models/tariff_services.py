from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import ArchivedAtMixin, CreatedAtMixin, IDIntMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models import Service, Tariff


class TariffService(IDIntMixin, CreatedAtMixin, UpdatedAtMixin, ArchivedAtMixin, Base):
    __tablename__ = "tariff_services"
    __table_args__ = (
        UniqueConstraint("service_id", "tariff_id", name="uq_tariff_service_service_tariff"),
    )

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Net price
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Tax amount
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Total

    # Foreign key fields
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    tariff_id: Mapped[int] = mapped_column(Integer, ForeignKey("tariffs.id", ondelete="CASCADE"))

    # Relationships
    service: Mapped["Service"] = relationship(back_populates="tariff_services")
    tariff: Mapped["Tariff"] = relationship(back_populates="tariff_services")

    def __init__(self, price: Decimal, tax: Decimal, total: Decimal, service_id: int, tariff_id: int):
        super().__init__()
        self.price = price
        self.tax = self.calculate_tax(price, tax)
        self.total = self.price + self.tax
        self.service_id = service_id
        self.tariff_id = tariff_id

    @staticmethod
    def calculate_tax(price: Decimal, tax: Decimal) -> Decimal:
        """Calculate tax based on price and tax"""
        return price * tax
