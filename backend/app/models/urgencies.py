from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Urgency(Base):
    __tablename__ = "urgencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    def __repr__(self):  # pragma: no cover
        return f"<Urgency {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "urgency"
