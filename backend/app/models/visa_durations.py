from sqlalchemy import Integer, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column

from app.database.custom_types import ChoiceType
from app.models.base import Base


class VisaDuration(Base):
    __tablename__ = "visa_durations"
    __table_args__ = (
        UniqueConstraint("term", "entry", name="uq_visa_duration_term_entry"),
    )

    TERM_1 = '1'
    TERM_3 = '3'
    TERM_6 = '6'
    TERM_12 = '12'
    TERM_24 = '24'
    TERM_36 = '36'
    TERM_48 = '48'
    TERM_60 = '60'
    TERM_120 = '120'
    TERM_CHOICES = (
        (TERM_1, '1 month'),
        (TERM_3, '3 months'),
        (TERM_6, '6 months'),
        (TERM_12, '1 year'),
        (TERM_24, '2 years'),
        (TERM_36, '3 years'),
        (TERM_48, '4 years'),
        (TERM_60, '5 years'),
        (TERM_120, '10 years'),
    )

    SINGLE_ENTRY = 'single_entry'
    DOUBLE_ENTRY = 'double_entry'
    MULTIPLE_ENTRY = 'multiple_entry'
    ENTRY_CHOICES = (
        (SINGLE_ENTRY, 'Single entry'),
        (DOUBLE_ENTRY, 'Double entry'),
        (MULTIPLE_ENTRY, 'Multiple entry')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    term: Mapped[str] = mapped_column(ChoiceType(TERM_CHOICES))
    entry: Mapped[str] = mapped_column(ChoiceType(ENTRY_CHOICES))

    def __repr__(self):
        return f'<VisaDuration(name={self.term}, term={self.entry})>'

    @staticmethod
    def get_model_type() -> str:
        return 'visa_duration'


@event.listens_for(VisaDuration, "before_insert")
@event.listens_for(VisaDuration, "before_update")
def generate_name_before_save(mapper, connection, target):
    term_map = dict(target.TERM_CHOICES)
    entry_map = dict(target.ENTRY_CHOICES)
    target.name = f"{term_map[target.term]} {entry_map[target.entry]}"
