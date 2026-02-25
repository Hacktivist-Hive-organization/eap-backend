# app/repositories/request_type_approver_repository.py
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.db_request_type_approver import DBRequestTypeApprover
from app.models.db_user import DbUser


class RequestTypeApproverRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_least_busy(self, request_type_id: int) -> DBRequestTypeApprover | None:
        """
        Return least busy approver for request_type_id
        Exclude users who are currently out of office
        """
        approvers = (
            self.db.query(DBRequestTypeApprover)
            .join(DbUser, DBRequestTypeApprover.user_id == DbUser.id)
            .filter(DBRequestTypeApprover.request_type_id == request_type_id)
            .filter(DbUser.is_out_of_office == False)
            .all()
        )

        if not approvers:
            return None

        # Pick least busy (lowest workload)
        min_workload = min(a.workload for a in approvers)
        candidates = [a for a in approvers if a.workload == min_workload]

        # Tie-breaker by id
        return sorted(candidates, key=lambda x: x.id)[0]

    def increment_workload(
        self, approver: DBRequestTypeApprover
    ) -> DBRequestTypeApprover:
        approver.increase_workload()
        self.db.add(approver)
        self.db.commit()
        self.db.refresh(approver)
        return approver
