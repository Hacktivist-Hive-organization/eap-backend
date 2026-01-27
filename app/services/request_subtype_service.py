# app/services/request_subtype_service.py
from app.repositories import RequestSubtypeRepository
from app.common.exceptions import BusinessException
from fastapi import status

class RequestSubtypeService:

    def __init__(self, repo: RequestSubtypeRepository):
        self.repo = repo

    def get_all(self):
        subtypes = self.repo.get_all()
        if not subtypes:
            raise BusinessException(message="No subtypes found", status_code=status.HTTP_404_NOT_FOUND)
        return subtypes
