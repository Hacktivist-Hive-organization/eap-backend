import sys
from pathlib import Path

# Get project root (3 levels up)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Insert at beginning so it has priority
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now imports from the project's root folder can be made
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


if __name__ == "__main__":
    run_seeds()
