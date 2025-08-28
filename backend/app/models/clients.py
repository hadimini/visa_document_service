from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin, IsActiveMixin

if TYPE_CHECKING:
    from app.models.tariffs import Tariff
    from app.models.users import User


class Client(CreatedAtMixin, UpdatedAtMixin, IsActiveMixin, Base):
    __tablename__ = "clients"

    TYPE_INDIVIDUAL = 'individual'
    TYPE_LEGAL = 'legal'

    TYPE_CHOICES = (
        (TYPE_INDIVIDUAL, 'Individual'),
        (TYPE_LEGAL, 'Legal'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tariff_id: Mapped[int] = mapped_column(Integer, ForeignKey("tariffs.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(ChoiceType(TYPE_CHOICES))

    tariff: Mapped["Tariff"] = relationship(back_populates="clients")

    employees: Mapped[list["User"]] = relationship(
        "User",
        back_populates="employee_client",
        foreign_keys="User.employee_client_id"
    )
    managers: Mapped[list["User"]] = relationship(
        "User",
        back_populates="manager_client",
        foreign_keys="User.manager_client_id"
    )
    individual: Mapped["User"] = relationship(
        "User",
        back_populates="individual_client",
        uselist=False,
        foreign_keys="User.individual_client_id"
    )

    def __repr__(self) -> str:
        return f"<Client {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "client"
