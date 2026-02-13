from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repo: HealthRepository):
        self.repo = repo

    def get_health(self):
        db_status = self.repo.get_health()
        return db_status
