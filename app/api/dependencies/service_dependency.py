from fastapi import Depends

from app.api.dependencies.repository_dependency import get_user_repository,get_health_repository
from app.services.health import HealthService
from app.services.user_service import UserService


def get_user_service(repo=Depends(get_user_repository)):
    return UserService(repo)

def get_health_service(repo=Depends(get_health_repository)):
    return HealthService(repo)