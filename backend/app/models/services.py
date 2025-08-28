from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


class Service(CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "services"

    FEE_TYPE_CENTER = "center"
    FEE_TYPE_CONSULAR = "consular"
    FEE_TYPE_DELIVERY = "delivery"
    FEE_TYPE_GENERAL = "general"
    FEE_TYPE_INVITATION = "invitation"
    FEE_TYPE_SERVICE_PROVIDER = "provider"

    FEE_TYPE_CHOICES = (
        (FEE_TYPE_CENTER, "Center"),
        (FEE_TYPE_CONSULAR, "Consular"),
        (FEE_TYPE_DELIVERY, "Delivery"),
        (FEE_TYPE_GENERAL, "General"),
        (FEE_TYPE_INVITATION, "Invitation"),
        (FEE_TYPE_SERVICE_PROVIDER, "Service Provider"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    fee_type: Mapped[str] = mapped_column(ChoiceType(FEE_TYPE_CHOICES))
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))

    # TODO
    # visa_type, duration, urgency

    def __repr__(self):
        return f"<Service {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "service"
