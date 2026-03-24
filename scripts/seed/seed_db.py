import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Project root
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / "app").exists():
    BASE_DIR = BASE_DIR.parent
sys.path.insert(0, str(BASE_DIR))

from app.database.session import SessionLocal
from scripts.seed.data.demo_data import seed_demo_data
from scripts.seed.data.request_type_approvers import seed_request_type_approvers
from scripts.seed.data.request_types import seed_request_type_subtype_data
from scripts.seed.data.users import seed_users


def run_seed(db: Session):
    seed_users(db)
    seed_request_type_subtype_data(db)
    seed_request_type_approvers(db)
    seed_demo_data()


def main():
    db: Session = SessionLocal()
    try:
        run_seed(db)
        print("Database seeding completed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
