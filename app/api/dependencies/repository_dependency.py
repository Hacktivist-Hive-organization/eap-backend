# app/api/dependencies/repository_dependency.py

from app.database.session import DBSession
from app.repositories import (
    HealthRepository,
    RequestRepository,
    RequestSubtypeRepository,
    RequestTrackingRepository,
    RequestTypeApproverRepository,
    RequestTypeRepository,
    UserRepository,
)


def get_user_repository(db: DBSession):
    return UserRepository(db)


def get_health_repository(db: DBSession):
    return HealthRepository(db)


def get_request_repository(db: DBSession):
    return RequestRepository(db)


def get_request_type_repository(db: DBSession):
    return RequestTypeRepository(db)


def get_request_subtype_repository(db: DBSession):
    return RequestSubtypeRepository(db)


def get_request_tracking_repository(db: DBSession):
    return RequestTrackingRepository(db)


def get_request_type_approver_repository(db: DBSession):
    return RequestTypeApproverRepository(db)
