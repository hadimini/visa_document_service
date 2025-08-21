from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.db import Base
from app.database.custom_types import ChoiceType


class User(Base):
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
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(ChoiceType(ROLE_CHOICES), nullable=False, server_default=ROLE_INDIVIDUAL)
    salt: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    entry_logs: Mapped[list["LogEntry"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "user"
