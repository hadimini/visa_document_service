import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import CreatedAtMixin


class BlackListToken(CreatedAtMixin, Base):
    __tablename__ = "blacklist_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    expire: Mapped[datetime]

    def __repr__(self):
        return f"<BlackListToken {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "black_list_token"
