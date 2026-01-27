# app/services/request_subtype_service.py
from fastapi import status

from app.common.exceptions import BusinessException
from app.repositories import RequestSubtypeRepository


class RequestSubtypeService:

    def __init__(self, repo: RequestSubtypeRepository):
        self.repo = repo

    def get_all(self):
        subtypes = self.repo.get_all()
        if not subtypes:
            raise BusinessException(
                message="No subtypes found", status_code=status.HTTP_404_NOT_FOUND
            )
        return subtypes
