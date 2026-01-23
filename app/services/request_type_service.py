# app/services/request_type_service.py
from app.common.exceptions import BusinessException
from app.repositories import RequestTypeRepository


class RequestTypeService:

    def __init__(self, repo:RequestTypeRepository):
        self.repo = repo

    def get_all(self):
        types =  self.repo.get_all()
        if not types:
            raise BusinessException("No request types found")
        return types
