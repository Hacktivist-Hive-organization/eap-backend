from app.database.session import SessionLocal
from scripts.seed.request_types import seed_request_type_subtype_data
from scripts.seed.users import seed_users


def run_seeds():
    db = SessionLocal()
    try:
        seed_users(db)
        seed_request_type_subtype_data(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
