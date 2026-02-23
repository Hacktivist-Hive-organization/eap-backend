# app/repositories/request_type_approver_repository.py
from sqlalchemy.orm import Session


class RequestTypeApproverRepository:
    def __init__(self, db: Session):
        self.db = db
