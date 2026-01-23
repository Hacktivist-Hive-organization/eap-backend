# app/services/request_subtype_service.py
from app.repositories import RequestSubtypeRepository
from app.common.exceptions import BusinessException

class RequestSubtypeService:

    def __init__(self, repo: RequestSubtypeRepository):
        self.repo = repo

    def get_all(self):
        subtypes = self.repo.get_all()
        if not subtypes:
            raise BusinessException("No subtypes found")
        return subtypes


