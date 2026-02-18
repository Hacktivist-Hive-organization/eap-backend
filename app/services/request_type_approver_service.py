# app/services/request_type_approver_service.py
from app.repositories import (
    RequestRepository,
    RequestTypeApproverRepository,
    RequestTypeRepository,
    UserRepository,
)


class RequestTypeApproverService:
    def __init__(
        self,
        repo: RequestTypeApproverRepository,
        type_repo: RequestTypeRepository,
        user_repo: UserRepository,
    ):
        self.repo = repo
        self.type_repo = type_repo
        self.user_repo = user_repo
