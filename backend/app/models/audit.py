from datetime import datetime
from enum import Enum

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.users import User


class Action(Enum):
    ACCESS = "access"
    ARCHIVE = "archive"
    DELETE = "delete"
    CREATE = "create"
    UPDATE = "update"


class LogEntry(Base):
    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    # The actor could be a system rather than a user, which is why it's nullable
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), nullable=True)
    action: Mapped[Action] = mapped_column(
        postgresql.ENUM(
            Action,
            name="action_enum",
            create_type=False
        ),
    )
    model_type: Mapped[str] = mapped_column(String(30), unique=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="log_entries")

    def __repr__(self):
        return "<LogEntry {}>".format(self.id)

    @staticmethod
    def get_model_type() -> str:
        return "log_entry"
