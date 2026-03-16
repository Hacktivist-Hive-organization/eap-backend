# app/api/dependencies/service_dependency.py

from functools import lru_cache

from fastapi import Depends

from app.api.dependencies.repository_dependency import (
    get_health_repository,
    get_request_repository,
    get_request_subtype_repository,
    get_request_tracking_repository,
    get_request_type_approver_repository,
    get_request_type_repository,
    get_user_repository,
)
from app.infrastructure.email.manager import EmailManager
from app.services import (
    AuthService,
    EmailService,
    HealthService,
    RequestService,
    RequestSubtypeService,
    RequestTrackingService,
    RequestTypeApproverService,
    RequestTypeService,
    UserService,
)


@lru_cache
def get_email_manager():
    return EmailManager()


def get_email_service(email_manager=Depends(get_email_manager)):
    return EmailService(email_manager)


def get_user_service(repo=Depends(get_user_repository)):
    return UserService(repo)


def get_auth_service(
    repo=Depends(get_user_repository),
    email_service=Depends(get_email_service),
):
    return AuthService(repo, email_service)


def get_health_service(repo=Depends(get_health_repository)):
    return HealthService(repo)


def get_request_service(
    request_repo=Depends(get_request_repository),
    type_repo=Depends(get_request_type_repository),
    subtype_repo=Depends(get_request_subtype_repository),
    approver_repo=Depends(get_request_type_approver_repository),
    tracking_repo=Depends(get_request_tracking_repository),
    email_service=Depends(get_email_service),
):
    return RequestService(
        request_repo=request_repo,
        type_repo=type_repo,
        subtype_repo=subtype_repo,
        email_service=email_service,
        approver_repo=approver_repo,
        tracking_repo=tracking_repo,
    )


def get_request_type_service(repo=Depends(get_request_type_repository)):
    return RequestTypeService(repo)


def get_request_subtype_service(repo=Depends(get_request_subtype_repository)):
    return RequestSubtypeService(repo)


def get_request_tracking_service(
    repo=Depends(get_request_tracking_repository),
    request_repo=Depends(get_request_repository),
):
    return RequestTrackingService(
        repo=repo,
        request_repo=request_repo,
    )


def get_request_type_approver_service(
    repo=Depends(get_request_type_approver_repository),
    type_repo=Depends(get_request_type_repository),
    user_repo=Depends(get_user_repository),
):
    return RequestTypeApproverService(repo, type_repo, user_repo)
