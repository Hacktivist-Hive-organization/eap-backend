from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings


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
    else:
        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        return engine, SessionLocal

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables() -> None:
    Base.metadata.create_all(bind=engine)

def drop_tables() -> None:
    Base.metadata.drop_all(bind=engine)

# SQLAlchemy DB URL
SQLALCHEMY_DATABASE_URL = create_database_url()

# engine + session
engine, SessionLocal = create_engine_and_session(SQLALCHEMY_DATABASE_URL)

DBSession = Annotated[Session, Depends(get_db)]

