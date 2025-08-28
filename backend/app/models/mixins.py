from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class CompletedAtMixin:
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )


class IsActiveMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
