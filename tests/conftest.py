# conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="function")
def db_session():
    Base = declarative_base()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()

        Base.metadata.drop_all(bind=engine)
