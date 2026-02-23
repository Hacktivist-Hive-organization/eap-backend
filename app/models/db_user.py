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
    is_out_of_office = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user_reqs = relationship(
        "DBRequest", foreign_keys="[DBRequest.requester_id]", back_populates="requester"
    )

    req_tracking = relationship(
        "DBRequestTracking",
        foreign_keys="[DBRequestTracking.user_id]",
        back_populates="user",
    )

    assigned_request_types = relationship(
        "DBRequestTypeApprover", back_populates="user", cascade="all, delete-orphan"
    )

    # Helper property to get actual RequestType objects
    @property
    def request_types_assigned(self):
        """Returns list of RequestType objects assigned to this user for approval"""
        return [assignment.request_type for assignment in self.assigned_request_types]

    @property
    def assigned_request_type_ids(self):
        """Returns list of request type IDs assigned to this user for approval"""
        return [
            assignment.request_type_id for assignment in self.assigned_request_types
        ]

    # Helper method to check if user can approve a specific request type
    def can_approve_request_type(self, request_type_id: int) -> bool:
        """Check if this user is assigned to approve the given request type"""
        return any(
            assignment.request_type_id == request_type_id
            for assignment in self.assigned_request_types
        )
