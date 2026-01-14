from app.database.session import DBSession
from app.repositories.health_repository import HealthRepository
from app.repositories.user_repository import UserRepository


def get_user_repository(db: DBSession):
    return UserRepository(db)

def get_health_repository(db:DBSession):
    return HealthRepository(db)