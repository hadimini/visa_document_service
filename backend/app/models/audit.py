from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.custom_types import ChoiceType
from app.models.base import Base


if TYPE_CHECKING:
    from app.models.users import User


class LogEntry(Base):
    __tablename__ = "log_entries"

    ACTION_ACCESS = "access"
    ACTION_ARCHIVE = "archive"
    ACTION_CREATE = "create"
    ACTION_DELETE = "delete"
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_REGISTER = "register"
    ACTION_UPDATE = "update"
    ACTION_VERIFY = "verify"

    ACTION_CHOICES = (
        (ACTION_ACCESS, "Access"),
        (ACTION_ARCHIVE, "Archive"),
        (ACTION_CREATE, "Create"),
        (ACTION_DELETE, "Delete"),
        (ACTION_LOGIN, "Login"),
        (ACTION_LOGOUT, "Logout"),
        (ACTION_REGISTER, "Register"),
        (ACTION_UPDATE, "Update"),
        (ACTION_VERIFY, "Verify"),
    )

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    # The actor could be a system rather than a user, which is why it's nullable
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(ChoiceType(ACTION_CHOICES))
    model_type: Mapped[str] = mapped_column(String(30), unique=False, nullable=True)
    target_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="entry_logs")

    def __repr__(self):  # pragma: no cover
        return "<LogEntry {}>".format(self.id)

    @staticmethod
    def get_model_type() -> str:
        return "log_entry"
