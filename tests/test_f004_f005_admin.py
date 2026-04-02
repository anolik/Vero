"""F004+F005: Tests for admin dashboard and session creation."""
import os
import sys

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


def _login(client):
    """Login via the form and return cookies."""
    resp = client.post(
        "/admin/login",
        data={"username": "admin", "password": "changeme"},
        follow_redirects=False,
    )
    return resp.cookies


def _authed_get(client, url):
    """GET with admin session cookie."""
    cookies = _login(client)
    return client.get(url, cookies=cookies)


def _authed_post(client, url, **kwargs):
    """POST with admin session cookie."""
    cookies = _login(client)
    return client.post(url, cookies=cookies, **kwargs)


# ── F004: Dashboard ──

def test_dashboard_requires_auth(client):
    """Dashboard should redirect to login when not authenticated."""
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


def test_dashboard_rejects_bad_credentials(client):
    """Bad credentials should show error."""
    resp = client.post(
        "/admin/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert "Identifiants invalides" in resp.text


def test_dashboard_accessible_with_auth(client):
    """Dashboard should be accessible after login."""
    resp = _authed_get(client, "/admin")
    assert resp.status_code == 200
    assert "Sessions" in resp.text


def test_dashboard_shows_sessions(client, db):
    """Dashboard should list created sessions."""
    _authed_post(client, "/admin/create",
        data={"firm_name": "Cabinet Alpha", "contact_name": "Marie", "contact_email": "m@a.ca"},
        follow_redirects=False,
    )
    resp = _authed_get(client, "/admin")
    assert "Cabinet Alpha" in resp.text
    assert "Marie" in resp.text


def test_dashboard_shows_status_badges(client, db):
    """Dashboard should show colored status badges."""
    _authed_post(client, "/admin/create",
        data={"firm_name": "Cabinet Beta", "contact_name": "Jean", "contact_email": "j@b.ca"},
        follow_redirects=False,
    )
    resp = _authed_get(client, "/admin")
    assert "En attente" in resp.text


def test_dashboard_has_copy_link_button(client, db):
    """Dashboard should have a copy link button for each session."""
    _authed_post(client, "/admin/create",
        data={"firm_name": "Cabinet Gamma", "contact_name": "Luc", "contact_email": "l@g.ca"},
        follow_redirects=False,
    )
    resp = _authed_get(client, "/admin")
    assert "Copier le lien" in resp.text
    assert "/form/" in resp.text


def test_dashboard_has_new_session_button(client):
    """Dashboard should have a link to create new session."""
    resp = _authed_get(client, "/admin")
    assert "Nouvelle session" in resp.text


# ── F005: Create session ──

def test_create_session_form_accessible(client):
    """Session creation form should be accessible."""
    resp = _authed_get(client, "/admin/create")
    assert resp.status_code == 200
    assert "Nom du cabinet" in resp.text


def test_create_session_requires_auth(client):
    """Session creation should require auth."""
    resp = client.post(
        "/admin/create",
        data={"firm_name": "X", "contact_name": "Y", "contact_email": "y@x.ca"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


def test_create_session_with_valid_data(client, db):
    """Valid data should create a session and redirect."""
    resp = _authed_post(client, "/admin/create",
        data={"firm_name": "Cabinet Delta", "contact_name": "Anne", "contact_email": "a@d.ca"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    conn = get_db(db)
    session = conn.execute("SELECT * FROM sessions WHERE firm_name = 'Cabinet Delta'").fetchone()
    conn.close()
    assert session is not None
    assert session["contact_name"] == "Anne"
    assert session["status"] == "pending"


def test_create_session_generates_unique_link(client, db):
    """Each created session should have a unique token in the dashboard."""
    for i in range(3):
        _authed_post(client, "/admin/create",
            data={"firm_name": f"Cab {i}", "contact_name": f"P{i}", "contact_email": f"p{i}@t.ca"},
            follow_redirects=False,
        )
    conn = get_db(db)
    tokens = conn.execute("SELECT token FROM sessions").fetchall()
    conn.close()
    token_list = [t["token"] for t in tokens]
    assert len(set(token_list)) == 3


# ── Login/Logout ──

def test_login_page_accessible(client):
    """Login page should be accessible."""
    resp = client.get("/admin/login")
    assert resp.status_code == 200
    assert "Se connecter" in resp.text


def test_logout_clears_session(client):
    """Logout should clear the session cookie."""
    cookies = _login(client)
    resp = client.get("/admin/logout", cookies=cookies, follow_redirects=False)
    assert resp.status_code == 303
    # After logout, dashboard should redirect to login
    resp2 = client.get("/admin", follow_redirects=False)
    assert resp2.status_code == 303
