import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base

IS_TESTING = os.getenv("TESTING") == "1"

if IS_TESTING:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
else:
    from sqlalchemy import URL
    from sqlalchemy_utils import create_database, database_exists

    def create_database_url() -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database=settings.DATABASE_NAME,
        )

    def create_engine_and_session(url: str | URL) -> tuple:
        try:
            if not database_exists(url):
                create_database(url)
            engine = create_engine(
                url,
                echo=settings.DATABASE_ECHO,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                future=True,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create DB engine or schema: {e}")
        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        return engine, SessionLocal

    SQLALCHEMY_DATABASE_URL = create_database_url()
    engine, SessionLocal = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


def create_tables() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS public;"))
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    Base.metadata.drop_all(bind=engine)
