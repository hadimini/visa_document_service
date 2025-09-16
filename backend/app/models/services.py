from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, IDIntMixin, UpdatedAtMixin, ArchivedAtMixin

if TYPE_CHECKING:
    from app.models import Country, TariffService, Urgency, VisaDuration, VisaType


class Service(ArchivedAtMixin, CreatedAtMixin, IDIntMixin, UpdatedAtMixin, Base):
    """Represents a service offered, including its fee type and associated entities.

        Attributes:
            name (Mapped[str]): The name of the service.
            fee_type (Mapped[str]): The type of fee associated with the service (consular or general).
            country_id (Mapped[int]): Foreign key referencing the associated country.
            urgency_id (Mapped[int]): Foreign key referencing the associated urgency.
            visa_duration_id (Mapped[int]): Foreign key referencing the associated visa duration.
            visa_type_id (Mapped[int]): Foreign key referencing the associated visa type.
            country (Mapped[Country]): Relationship to the Country model.
            tariff_services (Mapped[list[TariffService]]): Relationship to the TariffService model.
            urgency (Mapped[Urgency]): Relationship to the Urgency model.
            visa_duration (Mapped[VisaDuration]): Relationship to the VisaDuration model.
            visa_type (Mapped[VisaType]): Relationship to the VisaType model.
        """

    __tablename__ = "services"

    FEE_TYPE_CONSULAR = "consular"
    FEE_TYPE_GENERAL = "general"

    FEE_TYPE_CHOICES = (
        (FEE_TYPE_CONSULAR, "Consular"),
        (FEE_TYPE_GENERAL, "General"),
    )

    name: Mapped[str] = mapped_column(String)
    fee_type: Mapped[str] = mapped_column(ChoiceType(FEE_TYPE_CHOICES))

    # Foreign key fields
    country_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=True
    )
    urgency_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("urgencies.id", ondelete="CASCADE"), nullable=True
    )
    visa_duration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("visa_durations.id", ondelete="CASCADE"), nullable=True
    )
    visa_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("visa_types.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    country: Mapped["Country"] = relationship(back_populates="services")
    tariff_services: Mapped[list["TariffService"]] = relationship(
        back_populates="service",
        foreign_keys="TariffService.service_id",
        cascade="all, delete-orphan",
    )
    urgency: Mapped["Urgency"] = relationship(back_populates="services")
    visa_duration: Mapped["VisaDuration"] = relationship(back_populates="services")
    visa_type: Mapped["VisaType"] = relationship(back_populates="services")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "service"


@event.listens_for(Service, "before_update")
def set_updated_at(mapper, connection, target):
    """Automatically set the updated_at timestamp before any update to the Service instance.

    Args:
        mapper: The mapper associated with the Service class.
        connection: The database connection being used.
        target: The instance of the Service being updated.
    """
    target.updated_at = datetime.now()
