# scripts/seed/request_type_approvers_n.py

from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.models.db_request_type import DBRequestType
from app.models.db_request_type_approver import DBRequestTypeApprover
from app.models.db_user import DbUser


def seed_request_type_approvers(db: Session):
    if db.query(DBRequestTypeApprover).count() > 0:
        return

    types = db.query(DBRequestType).all()
    approvers = db.query(DbUser).filter(DbUser.role == UserRole.APPROVER).all()

    if len(approvers) < len(types) * 2:
        raise ValueError("Not enough approvers to assign 2 per type")

    for i, rt in enumerate(types):
        a1 = approvers[i * 2]
        a2 = approvers[i * 2 + 1]
        db.add_all(
            [
                DBRequestTypeApprover(request_type_id=rt.id, user_id=a1.id, workload=0),
                DBRequestTypeApprover(request_type_id=rt.id, user_id=a2.id, workload=0),
            ]
        )
    db.commit()
