# scripts/seed/reset_and_seed.py

import sys
from pathlib import Path

# setup project root
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / "app").exists():
    BASE_DIR = BASE_DIR.parent

sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import SessionLocal

# external demo data
from scripts.seed.demo_data import seed_demo_data

# base seeds
from scripts.seed.request_types import seed_request_type_subtype_data
from scripts.seed.users import seed_users


# reset database
def reset_database(db: Session):
    print("Resetting database...")

    tables = [
        "request_tracking",
        "requests",
        "request_type_approver",
        "request_subtype",
        "request_type",
        "users",
    ]

    for table in tables:
        try:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            print(f"Truncated: {table}")
        except Exception as e:
            db.rollback()
            print(f"Skip {table}: {e}")

    db.commit()
    print("Database reset complete")


# run all seeds
def run_seed(db: Session):
    print("Seeding base data...")

    # base data
    seed_users(db)
    seed_request_type_subtype_data(db)

    # demo data (comes from demo_data.py)
    seed_demo_data()

    print("All seeding complete")


# main
def main():
    db: Session = SessionLocal()

    try:
        reset_database(db)
        run_seed(db)
        print("\n✅ Reset and seed finished successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
