# db_user.py
from pycparser.c_ast import Default
from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database.session import Base
from app.models.db_mixins import TimestampMixin


class DbUser(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
