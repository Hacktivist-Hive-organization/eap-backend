from sqlalchemy import Column, Integer, String, Boolean
from app.database.session import Base


class DbUser(Base):
    __tablename__ = 'users'

    # Primary user fields
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
