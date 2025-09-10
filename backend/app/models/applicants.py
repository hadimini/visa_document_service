from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.custom_types import ChoiceType
from app.models.base import Base
from app.models.mixins import ArchivedAtMixin, IDIntMixin

if TYPE_CHECKING:
    from app.models import Order


class Applicant(ArchivedAtMixin, IDIntMixin, Base):
    __tablename__ = "applicants"

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    )

    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(ChoiceType(choices=GENDER_CHOICES))

    # One-to-one relationship
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        primary_key=True
    )

    # relationships
    order: Mapped["Order"] = relationship(back_populates="applicant")

    def __repr__(self) -> str:
        return f"<Applicant {self.first_name} {self.last_name}>"

    @staticmethod
    def get_model_type() -> str:
        return "applicant"
