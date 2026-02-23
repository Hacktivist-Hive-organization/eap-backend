# app/models/db_request_type_approver.py

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class DBRequestTypeApprover(Base):
    __tablename__ = "request_type_approvers"

    id = Column(Integer, primary_key=True)
    request_type_id = Column(
        Integer, ForeignKey("request_types.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workload = Column(Integer, nullable=False, default=0)
    last_assigned_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "request_type_id",
            "user_id",
            name="uq_request_type_user",
        ),
    )

    # relationships
    request_type = relationship("DBRequestType", back_populates="approvers")
    user = relationship("DbUser", back_populates="assigned_request_types")

    def increase_workload(self):
        """Increase workload when user gets a new request"""
        self.workload += 1
        self.last_assigned_at = func.now()

    def decrease_workload(self):
        """Decrease workload when user finishes a request"""
        if self.workload > 0:
            self.workload -= 1

    @property
    def is_available(self):
        # TODO: Add out_of_office check when feature is merged
        """Check if user can take more requests"""
        return self.workload < 5

    @property
    def is_available_without_ooo(self):
        """Separate property to check workload without OOO (for backward compatibility)"""
        return self.workload < 5
