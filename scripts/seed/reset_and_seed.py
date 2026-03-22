# scripts/seed/reset_and_seed.py

import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

# Project root
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / "app").exists():
    BASE_DIR = BASE_DIR.parent
sys.path.insert(0, str(BASE_DIR))

from app.database.session import SessionLocal
from scripts.seed.demo_data_n import seed_demo_data
from scripts.seed.request_type_approvers_n import seed_request_type_approvers
from scripts.seed.request_types_n import seed_request_type_subtype_data
from scripts.seed.users import seed_users


def reset_database(db: Session):
    tables = [
        "request_tracking",
        "requests",
        "request_type_approvers",
        "request_subtype",
        "request_type",
        "users",
    ]
    for table in tables:
        try:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
        except Exception:
            db.rollback()
    db.commit()


def run_seed(db: Session):
    seed_users(db)
    seed_request_type_subtype_data(db)
    seed_request_type_approvers(db)
    seed_demo_data()


def main():
    db: Session = SessionLocal()
    try:
        reset_database(db)
        run_seed(db)
        print("Database reset and seed completed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
