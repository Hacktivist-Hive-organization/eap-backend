from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.session import Base

class DbUser(Base):
    __tablename__ = 'users'

    # Primary user fields
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String,unique=True, nullable=False)

    user_reqs = relationship("DBRequest", foreign_keys="[DBRequest.requester_id]", back_populates="requester")

