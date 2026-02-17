# app/models/db_user.py

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.common.enums import UserRole
from app.database.base import Base
from app.models.db_mixins import TimestampMixin


class DbUser(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.REQUESTER)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    user_reqs = relationship(
        "DBRequest", foreign_keys="[DBRequest.requester_id]", back_populates="requester"
    )

    req_tracking = relationship(
        "DBRequestTracking",
        foreign_keys="[DBRequestTracking.user_id]",
        back_populates="user",
    )

    def __init__(
        self,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str,
        role: UserRole,
        is_active: bool = True,
    ):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.hashed_password = hashed_password
        self.role = role
        self.is_active = is_active
