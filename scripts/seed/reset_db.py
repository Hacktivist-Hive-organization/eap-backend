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


def main():
    db: Session = SessionLocal()
    try:
        reset_database(db)
        print("Database reset completed successfully")
    finally:
        db.close()


if __name__ == "__main__":
    main()
