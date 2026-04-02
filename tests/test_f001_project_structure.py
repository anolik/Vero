"""F001: Tests for project structure and FastAPI app initialization."""
import os
import sys
import tempfile
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from database import init_db, get_db


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


@pytest.fixture
def client(temp_db, monkeypatch):
    """Create a test client with a temporary database."""
    monkeypatch.setenv("DATABASE_PATH", temp_db)
    # Re-import to pick up the new env var
    import importlib
    import config
    importlib.reload(config)
    import database
    importlib.reload(database)
    from main import app
    return TestClient(app)


def test_fastapi_app_starts(client):
    """App should start without errors and serve the home page."""
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_has_bootstrap(client):
    """Home page should include Bootstrap 5 CSS."""
    response = client.get("/")
    assert "bootstrap" in response.text.lower()


def test_home_page_has_vero_branding(client):
    """Home page should display Vero branding."""
    response = client.get("/")
    assert "Vero" in response.text


def test_database_schema_creates(temp_db):
    """Database schema should create all required tables."""
    db = get_db(temp_db)
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [t["name"] for t in tables]
    db.close()

    assert "sessions" in table_names
    assert "form_data" in table_names
    assert "uploads" in table_names
    assert "consent_logs" in table_names
    assert "text_templates" in table_names


def test_database_foreign_keys_enabled(temp_db):
    """Foreign keys should be enabled."""
    db = get_db(temp_db)
    fk_status = db.execute("PRAGMA foreign_keys").fetchone()
    db.close()
    assert fk_status[0] == 1


def test_sessions_token_index_exists(temp_db):
    """Index on sessions.token should exist."""
    db = get_db(temp_db)
    indexes = db.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='sessions'"
    ).fetchall()
    index_names = [i["name"] for i in indexes]
    db.close()
    assert "idx_sessions_token" in index_names


def test_static_files_served(client):
    """Static CSS should be accessible."""
    response = client.get("/static/css/custom.css")
    assert response.status_code == 200


def test_admin_requires_auth(client):
    """Admin endpoint should require authentication."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303  # redirect to login
