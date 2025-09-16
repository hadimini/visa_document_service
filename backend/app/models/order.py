from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import (
    ArchivedAtMixin,
    CompletedAtMixin,
    CreatedAtMixin,
    IDIntMixin,
    UpdatedAtMixin
)

if TYPE_CHECKING:
    from app.models import Applicant, Client, Country, User, Urgency, VisaDuration, VisaType


class Order(ArchivedAtMixin, CompletedAtMixin, CreatedAtMixin, IDIntMixin, UpdatedAtMixin, Base):
    """Represents an order in the system.

    This class defines the structure of an order, including its status, relationships
    with other entities, and methods for managing order data.

    Attributes:
        status (Mapped[str]): The current status of the order.
        number (Mapped[str]): The unique identifier for the order.
        country_id (Mapped[int]): Foreign key referencing the associated country.
        client_id (Mapped[int]): Foreign key referencing the associated client.
        created_by_id (Mapped[int]): Foreign key referencing the user who created the order.
        urgency_id (Mapped[int]): Foreign key referencing the urgency level of the order.
        visa_duration_id (Mapped[int]): Foreign key referencing the duration of the visa.
        visa_type_id (Mapped[int]): Foreign key referencing the type of visa.
        country (Mapped[Country]): Relationship to the Country model.
        client (Mapped[Client]): Relationship to the Client model.
        created_by (Mapped[User]): Relationship to the User model.
        applicant (Mapped[Applicant]): Relationship to the Applicant model.
        urgency (Mapped[Urgency]): Relationship to the Urgency model.
        visa_duration (Mapped[VisaDuration]): Relationship to the VisaDuration model.
        visa_type (Mapped[VisaType]): Relationship to the VisaType model.
    """

    __tablename__ = "orders"

    STATUS_DRAFT = "draft"
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_NEW, "New"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status: Mapped[str] = mapped_column(ChoiceType(choices=STATUS_CHOICES), default=STATUS_DRAFT, server_default="draft")
    number: Mapped[str] = mapped_column(String, nullable=True)
    # Foreign key fields
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("countries.id", ondelete="CASCADE", name="orders_country_id_fkey")
    )
    client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE", name="orders_client_id_fkey")
    )
    created_by_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", name="orders_created_by_id_fkey")
    )
    urgency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("urgencies.id", ondelete="CASCADE", name="orders_urgency_id_fkey")
    )
    visa_duration_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("visa_durations.id", name="orders_visa_duration_id_fkey")
    )
    visa_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("visa_types.id", name="orders_visa_type_id_fkey")
    )

    # Relationships
    country: Mapped["Country"] = relationship(back_populates="orders")
    client: Mapped["Client"] = relationship(back_populates="orders")
    created_by: Mapped["User"] = relationship(back_populates="orders")
    applicant: Mapped["Applicant"] = relationship(
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )
    urgency: Mapped["Urgency"] = relationship()
    visa_duration: Mapped["VisaDuration"] = relationship()
    visa_type: Mapped["VisaType"] = relationship()

    def __repr__(self) -> str:
        """Return a string representation of the Order instance."""
        return f"<Order {self.number}>"

    @staticmethod
    def get_model_type() -> str:
        """Return the model type as a string.

        Returns:
            str: The type of the model, which is 'order'.
        """
        return "order"


@event.listens_for(Order, "after_insert")
def set_number(mapper, connection, target):
    """Automatically set number on order creation"""
    target.number = f"{target.created_at.year}-{target.id:04d}"
