# app/api/dependencies/service_dependency.py

from fastapi import Depends

from app.api.dependencies.repository_dependency import (
    get_health_repository,
    get_request_repository,
    get_request_subtype_repository,
    get_request_tracking_repository,
    get_request_type_repository,
    get_user_repository,
)
from app.infrastructure.email.manager import EmailManager
from app.services import (
    AuthService,
    HealthService,
    RequestService,
    RequestSubtypeService,
    RequestTrackingService,
    RequestTypeService,
    UserService,
)
from app.services.email_service import EmailService


def get_email_manager():
    return EmailManager()


def get_email_service(manager=Depends(get_email_manager)):
    return EmailService(manager)


def get_user_service(repo=Depends(get_user_repository)):
    return UserService(repo)


def get_auth_service(repo=Depends(get_user_repository)):
    return AuthService(repo)


def get_health_service(repo=Depends(get_health_repository)):
    return HealthService(repo)


def get_request_service(
    request_repo=Depends(get_request_repository),
    type_repo=Depends(get_request_type_repository),
    subtype_repo=Depends(get_request_subtype_repository),
):
    return RequestService(
        request_repo,
        type_repo,
        subtype_repo,
    )


def get_request_type_service(repo=Depends(get_request_type_repository)):
    return RequestTypeService(repo)


def get_request_subtype_service(repo=Depends(get_request_subtype_repository)):
    return RequestSubtypeService(repo)


def get_request_tracking_service(
    repo=Depends(get_request_tracking_repository),
    request_repo=Depends(get_request_repository),
):
    return RequestTrackingService(repo, request_repo)
