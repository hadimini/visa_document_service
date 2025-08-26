from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    alpha2: Mapped[str] = mapped_column(String)
    alpha3: Mapped[str] = mapped_column(String)
    available_for_order: Mapped[bool] = mapped_column(Boolean, default=False)
