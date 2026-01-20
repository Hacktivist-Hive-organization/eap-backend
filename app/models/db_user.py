from sqlalchemy import Column, Integer, String, Boolean
from app.database.session import Base
from app.models.mixins import TimestampMixin
from app.core.config import settings

class DbUser(TimestampMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': settings.DATABASE_SCHEMA}

    # Primary user fields
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
