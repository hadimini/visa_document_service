import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.db import Base


class BlackListToken(Base):
    __tablename__ = "blacklist_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    expire: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self):
        return f"<BlackListToken {self.id}>"

    @staticmethod
    def get_model_type() -> str:
        return "black_list_token"
