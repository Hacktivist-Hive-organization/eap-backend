# app/services/request_subtype_service.py
from app.repositories import RequestSubtypeRepository

class RequestSubtypeService:

    def __init__(self, repo: RequestSubtypeRepository):
        self.repo = repo

