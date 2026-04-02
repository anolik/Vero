"""F012-F020: Tests for Phase 4 — export, admin detail, landing, download, responsive."""
import json
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
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    import importlib
    import config
    importlib.reload(config)
    import database
    importlib.reload(database)
    init_db(db_path)
    return db_path


@pytest.fixture
def client(db, tmp_path):
    import importlib
    import routers.form as form_mod
    importlib.reload(form_mod)
    form_mod.UPLOADS_DIR = tmp_path / "uploads"
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient
    return TestClient(main.app)


AUTH = ("admin", "changeme")


def _create_completed_session(client, db):
    """Create a session and fill all steps through to completion."""
    # Create session via admin
    client.post(
        "/admin/create",
        data={"firm_name": "Cabinet Export", "contact_name": "Pierre Roy", "contact_email": "p@e.ca"},
        auth=AUTH,
    )
    conn = get_db(db)
    session = conn.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    token = session["token"]

    # Consent
    client.post(f"/form/{token}/consent", data={"consent_given": "true"})

    # Step 1: texts
    data = {}
    for cat in ["biography", "services", "client_approach", "credentials", "legal"]:
        data[f"{cat}_template"] = "1"
        data[f"{cat}_text"] = f"Texte pour {cat}"
    client.post(f"/form/{token}/step/1", data=data)

    # Step 2: identity
    client.post(f"/form/{token}/step/2", data={
        "first_name": "Pierre", "last_name": "Roy", "email": "pierre@export.ca"
    })

    # Step 3: branding
    client.post(f"/form/{token}/step/3", data={
        "primary_color": "#112233", "secondary_color": "#445566"
    })

    # Step 4: domain
    client.post(f"/form/{token}/step/4", data={
        "domain_option": "new", "domain_name": "pierre-roy.ca"
    })

    # Submit
    client.post(f"/form/{token}/submit")

    return session["id"], token


# ── F012: JSON export ──

class TestExportJSON:
    def test_export_returns_valid_json(self, client, db):
        sid, token = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}/export", auth=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "meta" in data
        assert "identity" in data
        assert "content" in data
        assert "branding" in data
        assert "domain" in data
        assert "privacy" in data

    def test_export_meta_section(self, client, db):
        sid, _ = _create_completed_session(client, db)
        data = client.get(f"/admin/sessions/{sid}/export", auth=AUTH).json()
        assert data["meta"]["schema_version"] == "1.0"
        assert data["meta"]["status"] == "completed"
        assert data["meta"]["firm_name"] == "Cabinet Export"

    def test_export_identity_section(self, client, db):
        sid, _ = _create_completed_session(client, db)
        data = client.get(f"/admin/sessions/{sid}/export", auth=AUTH).json()
        assert data["identity"]["first_name"] == "Pierre"
        assert data["identity"]["last_name"] == "Roy"

    def test_export_content_has_5_categories(self, client, db):
        sid, _ = _create_completed_session(client, db)
        data = client.get(f"/admin/sessions/{sid}/export", auth=AUTH).json()
        assert len(data["content"]) == 5
        for cat in ["biography", "services", "client_approach", "credentials", "legal"]:
            assert cat in data["content"]
            assert "final_text" in data["content"][cat]
            assert "selected_template" in data["content"][cat]

    def test_export_domain_section(self, client, db):
        sid, _ = _create_completed_session(client, db)
        data = client.get(f"/admin/sessions/{sid}/export", auth=AUTH).json()
        assert data["domain"]["requested_domain"] == "pierre-roy.ca"

    def test_export_privacy_section(self, client, db):
        sid, _ = _create_completed_session(client, db)
        data = client.get(f"/admin/sessions/{sid}/export", auth=AUTH).json()
        assert data["privacy"]["consent_given"] is True
        assert data["privacy"]["data_purpose"] == "website_creation"

    def test_export_incomplete_session_returns_400(self, client, db):
        # Create a session but don't complete it
        client.post(
            "/admin/create",
            data={"firm_name": "Incomplete", "contact_name": "X", "contact_email": "x@x.ca"},
            auth=AUTH,
        )
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE firm_name = 'Incomplete'").fetchone()
        conn.close()
        resp = client.get(f"/admin/sessions/{session['id']}/export", auth=AUTH)
        assert resp.status_code == 400

    def test_export_requires_auth(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}/export")
        assert resp.status_code == 401


# ── F019: Download JSON as file ──

class TestDownloadJSON:
    def test_download_has_content_disposition(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}/download", auth=AUTH)
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")

    def test_download_filename_format(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}/download", auth=AUTH)
        disposition = resp.headers.get("content-disposition", "")
        assert "Cabinet_Export" in disposition
        assert "Pierre_Roy" in disposition
        assert ".json" in disposition


# ── F017: Session detail ──

class TestSessionDetail:
    def test_detail_shows_session_info(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}", auth=AUTH)
        assert resp.status_code == 200
        assert "Cabinet Export" in resp.text
        assert "Pierre Roy" in resp.text

    def test_detail_shows_consent_info(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}", auth=AUTH)
        assert "Oui" in resp.text  # consent given

    def test_detail_requires_auth(self, client, db):
        sid, _ = _create_completed_session(client, db)
        resp = client.get(f"/admin/sessions/{sid}")
        assert resp.status_code == 401

    def test_detail_nonexistent_returns_404(self, client):
        resp = client.get("/admin/sessions/99999", auth=AUTH)
        assert resp.status_code == 404


# ── F018: Landing page ──

class TestLandingPage:
    def test_landing_page_accessible(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_landing_has_vero_branding(self, client):
        resp = client.get("/")
        assert "Vero" in resp.text

    def test_landing_has_admin_link(self, client):
        resp = client.get("/")
        assert "/admin" in resp.text


# ── F020: Responsive (Bootstrap grid presence) ──

class TestResponsive:
    def test_base_template_has_viewport_meta(self, client):
        resp = client.get("/")
        assert 'viewport' in resp.text

    def test_bootstrap_css_loaded(self, client):
        resp = client.get("/")
        assert 'bootstrap' in resp.text.lower()
