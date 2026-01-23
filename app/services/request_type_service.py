# app/services/request_type_service.py
from app.common.exceptions import BusinessException
from app.repositories import RequestTypeRepository


class RequestTypeService:

    def __init__(self, repo:RequestTypeRepository):
        self.repo = repo
