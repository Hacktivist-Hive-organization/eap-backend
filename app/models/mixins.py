# app/models/mixins.py

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    """Mixin to add created and updated timestamps to a table."""

    @declared_attr
    def created(cls):
        return Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)

    @declared_attr
    def updated(cls):
        return Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc),
                      nullable=False)
