from typing import TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.country_visas import CountryVisa


class VisaType(Base):
    __tablename__ = "visa_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    country_visas: Mapped[list["CountryVisa"]] = relationship(
        back_populates="visa_type",
        foreign_keys="CountryVisa.visa_type_id"
    )

    def __repr__(self):  # pragma: no cover
        return f"<VisaType: {self.name}>"

    @staticmethod
    def get_model_type() -> str:
        return "visa_type"
