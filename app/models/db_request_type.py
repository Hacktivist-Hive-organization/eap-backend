from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class DBRequestType(Base):
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # relationships
    subtypes = relationship("DBRequestSubtype", back_populates="type")
    approvers = relationship(
        "DBRequestTypeApprover",
        back_populates="request_type",
        cascade="all, delete-orphan",
    )

    # Helper property to get actual User objects
    @property
    def approver_users(self):
        """Returns list of User objects who are approvers for this request type"""
        return [approver.user for approver in self.approvers]

    @property
    def approver_user_ids(self):
        """Returns list of user IDs who are approvers for this request type"""
        return [approver.user_id for approver in self.approvers]
