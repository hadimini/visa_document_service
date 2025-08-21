from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Tariff(Base):
    __tablename__ = "tariffs"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return "<Tariff {}>".format(self.id)

    @staticmethod
    def get_model_type() -> str:
        return "tariff"
