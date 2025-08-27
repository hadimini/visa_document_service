from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base

if TYPE_CHECKING:
    from app.models.countries import Country
    from app.models.visa_types import VisaType


class CountryVisa(Base):
    __tablename__ = "country_visas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    visa_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("visa_types.id", ondelete="CASCADE"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true')

    country: Mapped["Country"] = relationship(back_populates="country_visas")
    visa_type: Mapped["VisaType"] = relationship(back_populates="country_visas")

    def __repr__(self):
        return f"<CountryVisa {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "country_visa"
