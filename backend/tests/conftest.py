"""
Pytest fixtures for backend tests.

Uses an in-memory SQLite database instead of PostgreSQL so tests can
run without any external service. This is a deliberate testing-only
substitution; production always uses PostgreSQL per DATABASE_URL.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.database import Base
from app.db.session import get_db
from app.main import app
from app import models  # noqa: F401  ensures models are registered on Base.metadata


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def anon_client(db_session):
    """An unauthenticated TestClient — use this to test auth itself
    (register/login/401 handling) or multi-user isolation."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(anon_client):
    """A TestClient that's already registered + logged in as a default
    test user (auth cookies persist across requests on this client
    instance). Every Phase 1/2 test uses this, since those tests are
    about project/scan/finding behavior, not auth itself."""
    anon_client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
        },
    )
    return anon_client
