from typing import TYPE_CHECKING

from app.models.base import Base
from app.models.mixins import ArchivedAtMixin, CreatedAtMixin, UpdatedAtMixin


if TYPE_CHECKING:
    from app.models import Service, Tariff


class TariffService(Base):
    pass
