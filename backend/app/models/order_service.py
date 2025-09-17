from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.helpers import calculate_tax
from app.models.base import Base
from app.models.mixins import IDIntMixin

if TYPE_CHECKING:
    from app.models import Order, Service


class OrderService(IDIntMixin, Base):
    __tablename__ = "order_services"

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Net price
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Tax / 100
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Tax amount
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Total

    # Foreign key fields
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE", name="order_service_order_id_fkey")
    )
    service_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE", name="order_service_service_id_fkey")
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="order_services")
    service: Mapped["Service"] = relationship()

    def __init__(self, price: Decimal, tax: Decimal, order_id: int, service_id: int):
        super().__init__()
        self.price = price
        self.tax = tax
        self.tax_amount = self.calculate_tax(price, tax)
        self.total = self.price + self.tax_amount
        self.order_id = order_id
        self.service_id = service_id

    def __repr__(self) -> str:
        return "<OrderService(price={}, tax={}, order_id={}, service_id={})>".format(
            self.price,
            self.tax,
            self.order_id,
            self.service_id
        )

    @staticmethod
    def calculate_tax(price: Decimal, tax: Decimal) -> Decimal:
        """Calculate tax based on price and tax"""
        return calculate_tax(price, tax)

    @staticmethod
    def get_model_type() -> str:
        return "tariff_service"
