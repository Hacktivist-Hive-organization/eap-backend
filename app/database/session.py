from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.engine import URL

from app.core.config import settings


Base = declarative_base()


# -------------------------------------------------
# Database URL builder
# -------------------------------------------------
def create_database_url() -> str | URL:
    """
    Build database URL based on DATABASE_TYPE.
    Supports PostgreSQL (prod) and SQLite (tests / CI).
    """

    if settings.DATABASE_TYPE.lower() == "sqlite":
        # SQLite (used for tests & CI)
        # Examples:
        #   sqlite:///:memory:
        #   sqlite:///./test.db
        return f"sqlite:///{settings.DATABASE_SCHEMA}"

    # PostgreSQL (default / production)
    return URL.create(
        drivername="postgresql+psycopg2",
        username=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_SCHEMA,
    )


# -------------------------------------------------
# Engine & session factory
# -------------------------------------------------
def create_engine_and_session(url: str | URL):
    try:
        if settings.DATABASE_TYPE.lower() == "sqlite":
            engine = create_engine(
                url,
                connect_args={"check_same_thread": False},
                echo=settings.DATABASE_ECHO,
                future=True,
            )
        else:
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
        raise RuntimeError(f"Failed to create DB engine: {e}")

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    return engine, SessionLocal


# -------------------------------------------------
# Create engine + session
# -------------------------------------------------
SQLALCHEMY_DATABASE_URL = create_database_url()
engine, SessionLocal = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


# -------------------------------------------------
# Dependency
# -------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


# -------------------------------------------------
# Helpers for app lifecycle
# -------------------------------------------------
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    Base.metadata.drop_all(bind=engine)

# SQLAlchemy DB URL
SQLALCHEMY_DATABASE_URL = create_database_url()


