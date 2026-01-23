import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.database.session import SessionLocal, engine, get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def ensure_test_schema():
    schema = getattr(settings, "DATABASE_SCHEMA", None)

    if not schema:
        return

    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        conn.execute(text(f'SET search_path TO "{schema}"'))
        conn.commit()


def truncate_all_tables(conn):

    tables = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = current_schema()
            """)).all()
    for (table_name,) in tables:
        conn.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE'))


@pytest.fixture(scope="function")
def db_session():
    # 🔹 Clear all tables BEFORE test
    with engine.begin() as conn:
        truncate_all_tables(conn)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        # 🔹 Clear all tables AFTER test
        with engine.begin() as conn:
            truncate_all_tables(conn)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
