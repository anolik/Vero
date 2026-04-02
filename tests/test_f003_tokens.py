"""F003: Tests for UUID token system — generation, validation, expiration."""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_db


@pytest.fixture
def db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DATABASE_PATH", db_path)
    import importlib
    import config
    importlib.reload(config)
    import database
    importlib.reload(database)
    init_db(db_path)
    return db_path


@pytest.fixture
def client(db):
    import importlib
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _create_session(db_path, token=None, expires_days=30, status="pending"):
    """Helper to insert a session directly into the database."""
    if token is None:
        token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    conn = get_db(db_path)
    conn.execute(
        """INSERT INTO sessions (token, firm_name, contact_name, contact_email, status, expires_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (token, "Cabinet Test", "Jean Dupont", "jean@test.ca", status, expires_at.isoformat()),
    )
    conn.commit()
    conn.close()
    return token


# ── Token generation tests ──

def test_token_is_valid_uuid4(db):
    """Generated token should be a valid UUID4."""
    token = _create_session(db)
    parsed = uuid.UUID(token, version=4)
    assert str(parsed) == token


def test_tokens_are_unique(db):
    """Each session should get a unique token."""
    t1 = _create_session(db)
    t2 = _create_session(db)
    assert t1 != t2


# ── Token validation tests ──

def test_valid_token_returns_200(client, db):
    """A valid, non-expired token should return 200."""
    token = _create_session(db)
    response = client.get(f"/form/{token}")
    assert response.status_code == 200


def test_invalid_token_returns_404(client):
    """An invalid token should return 404."""
    response = client.get("/form/not-a-real-token")
    assert response.status_code == 404


def test_nonexistent_uuid_returns_404(client):
    """A well-formed UUID that doesn't exist should return 404."""
    fake = str(uuid.uuid4())
    response = client.get(f"/form/{fake}")
    assert response.status_code == 404


def test_expired_token_returns_410(client, db):
    """An expired token should return 410 Gone."""
    token = _create_session(db, expires_days=-1)
    response = client.get(f"/form/{token}")
    assert response.status_code == 410


def test_token_with_future_expiry_works(client, db):
    """A token expiring in the future should work."""
    token = _create_session(db, expires_days=60)
    response = client.get(f"/form/{token}")
    assert response.status_code == 200


# ── Admin session creation tests ──

def test_admin_create_session_redirects(client):
    """Creating a session via admin should redirect to dashboard."""
    response = client.post(
        "/admin/create",
        data={"firm_name": "Cabinet X", "contact_name": "Marie", "contact_email": "m@x.ca"},
        auth=("admin", "changeme"),
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"


def test_admin_create_session_inserts_db(client, db):
    """Creating a session should insert a record with a UUID token."""
    client.post(
        "/admin/create",
        data={"firm_name": "Cabinet Y", "contact_name": "Pierre", "contact_email": "p@y.ca"},
        auth=("admin", "changeme"),
    )
    conn = get_db(db)
    sessions = conn.execute("SELECT * FROM sessions WHERE firm_name = 'Cabinet Y'").fetchall()
    conn.close()
    assert len(sessions) == 1
    uuid.UUID(sessions[0]["token"], version=4)  # Should not raise


def test_admin_create_session_sets_expiry(client, db):
    """Created session should have an expiration date in the future."""
    client.post(
        "/admin/create",
        data={"firm_name": "Cabinet Z", "contact_name": "Luc", "contact_email": "l@z.ca"},
        auth=("admin", "changeme"),
    )
    conn = get_db(db)
    session = conn.execute("SELECT * FROM sessions WHERE firm_name = 'Cabinet Z'").fetchone()
    conn.close()
    expires = datetime.fromisoformat(session["expires_at"])
    assert expires > datetime.now(timezone.utc)
