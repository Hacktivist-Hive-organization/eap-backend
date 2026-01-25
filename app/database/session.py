from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create Postgres DB only if needed
if settings.DATABASE_TYPE.lower() != "sqlite" and not database_exists(
    SQLALCHEMY_DATABASE_URL
):
    create_database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=10 if settings.DATABASE_TYPE.lower() != "sqlite" else 0,
    max_overflow=20 if settings.DATABASE_TYPE.lower() != "sqlite" else 0,
    pool_timeout=30 if settings.DATABASE_TYPE.lower() != "sqlite" else 0,
    pool_recycle=3600 if settings.DATABASE_TYPE.lower() != "sqlite" else 0,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

DBSession = Annotated[Session, Depends(lambda: SessionLocal())]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)
