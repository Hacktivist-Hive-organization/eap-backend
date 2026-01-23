# db_user.py

from sqlalchemy import Boolean, Column, Integer, String

from app.database.session import Base
from app.models.db_mixins import TimestampMixin


class DbUser(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)

    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
