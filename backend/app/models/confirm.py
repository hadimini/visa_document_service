import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import CreatedAtMixin, CompletedAtMixin

if TYPE_CHECKING:
    from app.models.users import User


class EmailConfirm(CompletedAtMixin, CreatedAtMixin, Base):
    __tablename__ = "email_confirm"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False)


    user: Mapped["User"] = relationship(back_populates="email_confirms")

    def __repr__(self):
        return f"<EmailConfirm {self.email}>"

    @staticmethod
    def get_model_type() -> str:
        return "email_confirm"


class PasswordResetConfirm(CreatedAtMixin, CompletedAtMixin, Base):
    __tablename__ = "password_reset_confirm"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(back_populates="password_reset_confirms")

    def __repr__(self):
        return f"<PasswordResetConfirm {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "password_reset_confirm"
