from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.database.db import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


if TYPE_CHECKING:
    from app.models.audit import LogEntry
    from app.models.clients import Client


class User(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "users"

    ROLE_ADMIN: str = "admin"
    ROLE_EMPLOYEE: str = "employee"
    ROLE_INDIVIDUAL: str = "individual"
    ROLE_MANAGER: str = "manager"
    ROLE_OPERATOR: str = "operator"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "admin"),
        (ROLE_EMPLOYEE, "Employee"),
        (ROLE_INDIVIDUAL, "Individual"),
        (ROLE_MANAGER, "Manager"),
        (ROLE_OPERATOR, "Operator"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(ChoiceType(ROLE_CHOICES), nullable=False, server_default=ROLE_INDIVIDUAL)
    salt: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    employee_client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)
    manager_client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)
    individual_client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)

    entry_logs: Mapped[list["LogEntry"]] = relationship(back_populates="user")
    employee_client: Mapped["Client"] = relationship(
        "Client", back_populates="employees", foreign_keys=employee_client_id
    )
    manager_client: Mapped["Client"] = relationship(
        "Client", back_populates="managers", foreign_keys=manager_client_id
    )
    individual_client: Mapped["Client"] = relationship(
        "Client",
        back_populates="individual",
        foreign_keys=individual_client_id
    )

    def __repr__(self):
        return f"<User {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "user"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
