from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class ArchivedAtMixin:
    archived_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IDIntMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class CompletedAtMixin:
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )


class IsActiveMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
