import pytest
from fastapi.testclient import TestClient
from app.config import database as db_module
from app.config.database import engine, get_db
from sqlalchemy.orm import sessionmaker
from main import app


@pytest.fixture(scope="function", autouse=True)
def db_session():
    """Provide a transactional scope around a test.

    - starts a DB connection and transaction
    - binds a Session to that connection
    - overrides app dependency get_db to yield the test session
    - patches db_module.SessionLocal to return sessions bound to the test connection
    - rolls back at teardown so no DB changes persist
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestSession()

    # Patch SessionLocal and get_db dependency
    orig_sessionlocal = db_module.SessionLocal
    db_module.SessionLocal = TestSession

    def _get_test_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db

    try:
        yield session
    finally:
        # rollback any changes and cleanup
        try:
            session.close()
        finally:
            transaction.rollback()
            connection.close()
            # restore original objects
            db_module.SessionLocal = orig_sessionlocal
            app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client():
    return TestClient(app)
