# app/services/request_type_service.py
from app.common.exceptions import BusinessException
from app.repositories import RequestTypeRepository
from fastapi import status


class RequestTypeService:

    def __init__(self, repo:RequestTypeRepository):
        self.repo = repo

    def get_all(self):
        types =  self.repo.get_all()
        if not types:
            raise BusinessException(message="No request types found", status_code=status.HTTP_404_NOT_FOUND)
        return types
