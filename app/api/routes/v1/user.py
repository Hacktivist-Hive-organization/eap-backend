from fastapi import Depends, APIRouter

from app.api.dependencies.service_dependency import get_user_service
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])

@router.get('/{id}', summary='')
def get_userinfo(id: int, service: UserService = Depends(get_user_service)):
    data =  service.get_userinfo( user_id=id)
