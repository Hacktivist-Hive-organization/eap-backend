# app/services/request_service.py
from app.common.exceptions import BusinessException
from app.models import DBRequest
from app.common.enums import Status
from app.repositories import RequestSubtypeRepository ,RequestTypeRepository , RequestRepository

class RequestService:

    def __init__(
        self,
        request_repo: RequestRepository,
        type_repo: RequestTypeRepository,
        subtype_repo: RequestSubtypeRepository
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo

    def _validate_type_and_subtype(self, type_id: int, subtype_id: int):
        """
        Private helper to validate:
        1. Type exists
        2. Subtype belongs to type
        Raises BusinessException if invalid.
        """
        if not self.type_repo.get_by_id(type_id):
            raise BusinessException(
                f'Request type not found: no type exists with id {type_id}')

        if not self.subtype_repo.get_by_id_and_type(subtype_id, type_id):
            raise BusinessException(f'Request subtype mismatch: '
                                    f'no subtype with id {subtype_id} belongs to type {type_id}')

    def create_request(self, request_in):

        self._validate_type_and_subtype(request_in.type_id,
                                        request_in.subtype_id)
        db_request = DBRequest(
            type_id=request_in.type_id,
            subtype_id=request_in.subtype_id,
            title=request_in.title,
            description=request_in.description,
            business_justification=request_in.business_justification,
            priority=request_in.priority,
            status=Status.DRAFT,
        )

        return self.request_repo.create(db_request)
