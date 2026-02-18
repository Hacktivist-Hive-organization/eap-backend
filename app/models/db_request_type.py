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

    def get_best_approver(self) -> int | None:
        """
        Select the best approver:
        1. select approvers with is_out_of_office == false
        1. then: approvers with workload < 5 (lowest workload wins)
        2. If all are at 5: pick the one who got their last request longest ago
        """
        # TODO: Add out_of_office filter feature is merged
        # active_approvers = [a for a in self.approvers if not
        # a.user.is.out_of_office]
        active_approvers = self.approvers  # For now, use all approvers

        # Check if anyone has workload less than 5
        available_approvers = [a for a in active_approvers if a.workload < 5]

        if available_approvers:  # FIXED: was checking active_approvers
            # Find lowest workload
            min_workload = min(a.workload for a in available_approvers)
            # Get all with lowest workload
            candidates = [a for a in available_approvers if a.workload == min_workload]

            if len(candidates) == 1:
                return candidates[0].user_id

            # If tie, pick least recently used
            candidates_with_time = [
                (a, a.last_assigned_at or datetime.min.replace(tzinfo=timezone.utc))
                for a in candidates
            ]
            oldest = min(candidates_with_time, key=lambda x: x[1])
            return oldest[0].user_id

        # Everyone is at max workload (5) - pick least recently used
        if active_approvers:
            candidates_with_time = [
                (a, a.last_assigned_at or datetime.min.replace(tzinfo=timezone.utc))
                for a in active_approvers
                # FIXED: was using self.approvers directly
            ]
            oldest = min(candidates_with_time, key=lambda x: x[1])
            return oldest[0].user_id

        return None
