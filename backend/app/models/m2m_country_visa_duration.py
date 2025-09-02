from sqlalchemy import Column, Table, Integer, ForeignKey

from app.models.base import Base


country_visa_duration = Table(
    "country_visa_duration",
    Base.metadata,
    Column(
        "country_visa_id",
        Integer,
        ForeignKey("country_visas.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "visa_duration_id",
        Integer,
        ForeignKey("visa_durations.id", ondelete="CASCADE"),
        primary_key=True
    )
)
