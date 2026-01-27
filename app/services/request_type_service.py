# app/services/request_type_service.py
from fastapi import status

from app.common.exceptions import BusinessException
from app.repositories import RequestTypeRepository


class RequestTypeService:

    def __init__(self, repo: RequestTypeRepository):
        self.repo = repo

    def get_all(self):
        types = self.repo.get_all()
        if not types:
            raise BusinessException(
                message="No request types found", status_code=status.HTTP_404_NOT_FOUND
            )
        return types
