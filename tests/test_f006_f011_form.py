"""F006-F011: Tests for the representative form wizard."""
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
    # Create uploads dir
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
def client(db, tmp_path, monkeypatch):
    # Patch UPLOADS_DIR so tests don't write to project uploads/
    import importlib
    import routers.form as form_mod
    importlib.reload(form_mod)
    form_mod.UPLOADS_DIR = tmp_path / "uploads"
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _create_session(db_path, expires_days=30):
    """Insert a test session and return its token."""
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    conn = get_db(db_path)
    conn.execute(
        """INSERT INTO sessions (token, firm_name, contact_name, contact_email, status, expires_at)
           VALUES (?, ?, ?, ?, 'pending', ?)""",
        (token, "Cabinet Test", "Jean Dupont", "jean@test.ca", expires_at.isoformat()),
    )
    conn.commit()
    conn.close()
    return token


def _give_consent(client, token):
    """Complete the consent step."""
    client.post(
        f"/form/{token}/consent",
        data={"consent_given": "true"},
        follow_redirects=False,
    )


def _fill_step1(client, token):
    """Fill step 1 with text selections."""
    data = {}
    for cat in ["biography", "services", "client_approach", "credentials", "legal"]:
        data[f"{cat}_template"] = "1"
        data[f"{cat}_text"] = f"Texte personnalisé pour {cat}"
    client.post(f"/form/{token}/step/1", data=data, follow_redirects=False)


def _fill_step2(client, token):
    """Fill step 2 with identity info."""
    client.post(
        f"/form/{token}/step/2",
        data={"first_name": "Marie", "last_name": "Tremblay", "email": "marie@test.ca"},
        follow_redirects=False,
    )


def _fill_step3(client, token):
    """Fill step 3 with colors (no logo)."""
    client.post(
        f"/form/{token}/step/3",
        data={"primary_color": "#1A3C5E", "secondary_color": "#C8A84B"},
        follow_redirects=False,
    )


def _fill_step4(client, token):
    """Fill step 4 with domain."""
    client.post(
        f"/form/{token}/step/4",
        data={"domain_option": "new", "domain_name": "marie-tremblay.ca"},
        follow_redirects=False,
    )


# ── F006: Consent ──

class TestConsent:
    def test_first_visit_shows_consent(self, client, db):
        token = _create_session(db)
        resp = client.get(f"/form/{token}")
        assert resp.status_code == 200
        assert "consentement" in resp.text.lower() or "J'accepte" in resp.text

    def test_consent_post_redirects_to_step1(self, client, db):
        token = _create_session(db)
        resp = client.post(
            f"/form/{token}/consent",
            data={"consent_given": "true"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/step/1" in resp.headers["location"]

    def test_consent_saved_in_db(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE token = ?", (token,)).fetchone()
        consent = conn.execute(
            "SELECT * FROM consent_logs WHERE session_id = ?", (session["id"],)
        ).fetchone()
        conn.close()
        assert consent is not None
        assert consent["consent_given"] == 1
        assert consent["consent_ip_hash"] is not None

    def test_already_consented_skips_consent(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.get(f"/form/{token}", follow_redirects=False)
        assert resp.status_code == 303
        assert "/step/" in resp.headers["location"]


# ── F007: Text selection ──

class TestStep1Texts:
    def test_step1_shows_categories(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.get(f"/form/{token}/step/1")
        assert resp.status_code == 200
        # Should mention at least some categories
        text = resp.text.lower()
        assert "biographie" in text or "biography" in text

    def test_step1_post_saves_data(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE token = ?", (token,)).fetchone()
        data = conn.execute(
            "SELECT * FROM form_data WHERE session_id = ? AND step = 1", (session["id"],)
        ).fetchall()
        conn.close()
        assert len(data) >= 5  # At least 5 categories saved

    def test_step1_post_redirects_to_step2(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        data = {}
        for cat in ["biography", "services", "client_approach", "credentials", "legal"]:
            data[f"{cat}_template"] = "1"
            data[f"{cat}_text"] = "text"
        resp = client.post(f"/form/{token}/step/1", data=data, follow_redirects=False)
        assert resp.status_code == 303
        assert "/step/2" in resp.headers["location"]


# ── F008: Identity ──

class TestStep2Identity:
    def test_step2_shows_form(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.get(f"/form/{token}/step/2")
        assert resp.status_code == 200
        assert "name" in resp.text.lower() or "nom" in resp.text.lower()

    def test_step2_saves_identity(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step2(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE token = ?", (token,)).fetchone()
        data = conn.execute(
            "SELECT field_key, field_value FROM form_data WHERE session_id = ? AND step = 2",
            (session["id"],),
        ).fetchall()
        conn.close()
        data_dict = {d["field_key"]: d["field_value"] for d in data}
        assert data_dict.get("first_name") == "Marie"
        assert data_dict.get("last_name") == "Tremblay"

    def test_step2_redirects_to_step3(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.post(
            f"/form/{token}/step/2",
            data={"first_name": "Luc", "last_name": "Roy", "email": "l@r.ca"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/step/3" in resp.headers["location"]


# ── F009: Branding ──

class TestStep3Branding:
    def test_step3_shows_form(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.get(f"/form/{token}/step/3")
        assert resp.status_code == 200
        assert "color" in resp.text.lower() or "couleur" in resp.text.lower()

    def test_step3_saves_colors(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step3(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE token = ?", (token,)).fetchone()
        data = conn.execute(
            "SELECT field_key, field_value FROM form_data WHERE session_id = ? AND step = 3",
            (session["id"],),
        ).fetchall()
        conn.close()
        data_dict = {d["field_key"]: d["field_value"] for d in data}
        assert data_dict.get("primary_color") == "#1A3C5E"

    def test_step3_redirects_to_step4(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.post(
            f"/form/{token}/step/3",
            data={"primary_color": "#000000", "secondary_color": "#FFFFFF"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/step/4" in resp.headers["location"]


# ── F010: Domain ──

class TestStep4Domain:
    def test_step4_shows_form(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.get(f"/form/{token}/step/4")
        assert resp.status_code == 200
        assert "domaine" in resp.text.lower() or "domain" in resp.text.lower()

    def test_step4_saves_domain(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step4(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT id FROM sessions WHERE token = ?", (token,)).fetchone()
        data = conn.execute(
            "SELECT field_key, field_value FROM form_data WHERE session_id = ? AND step = 4",
            (session["id"],),
        ).fetchall()
        conn.close()
        data_dict = {d["field_key"]: d["field_value"] for d in data}
        assert data_dict.get("domain_name") == "marie-tremblay.ca"
        assert data_dict.get("domain_option") == "new"

    def test_step4_redirects_to_confirmation(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        resp = client.post(
            f"/form/{token}/step/4",
            data={"domain_option": "existing", "domain_name": "existing.ca"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert "/confirmation" in resp.headers["location"]


# ── F011: Confirmation & Submit ──

class TestConfirmation:
    def test_confirmation_shows_recap(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        _fill_step2(client, token)
        _fill_step3(client, token)
        _fill_step4(client, token)
        resp = client.get(f"/form/{token}/confirmation")
        assert resp.status_code == 200
        assert "Marie" in resp.text or "Tremblay" in resp.text

    def test_confirmation_has_modify_buttons(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        _fill_step2(client, token)
        _fill_step3(client, token)
        _fill_step4(client, token)
        resp = client.get(f"/form/{token}/confirmation")
        assert "Modifier" in resp.text or "modifier" in resp.text

    def test_submit_marks_session_completed(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        _fill_step2(client, token)
        _fill_step3(client, token)
        _fill_step4(client, token)
        resp = client.post(f"/form/{token}/submit", follow_redirects=False)
        # Should redirect to thank you page or return 200
        assert resp.status_code in (200, 303)
        conn = get_db(db)
        session = conn.execute("SELECT status FROM sessions WHERE token = ?", (token,)).fetchone()
        conn.close()
        assert session["status"] == "completed"

    def test_session_status_updates_to_in_progress(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        conn = get_db(db)
        session = conn.execute("SELECT status FROM sessions WHERE token = ?", (token,)).fetchone()
        conn.close()
        assert session["status"] == "in_progress"


# ── F015-prep: Session resumption ──

class TestSessionResumption:
    def test_returning_user_skips_consent(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        # Return to the form entry
        resp = client.get(f"/form/{token}", follow_redirects=False)
        assert resp.status_code == 303
        # Should redirect to step 2 (next incomplete)
        assert "/step/2" in resp.headers["location"]

    def test_all_steps_complete_redirects_to_confirmation(self, client, db):
        token = _create_session(db)
        _give_consent(client, token)
        _fill_step1(client, token)
        _fill_step2(client, token)
        _fill_step3(client, token)
        _fill_step4(client, token)
        resp = client.get(f"/form/{token}", follow_redirects=False)
        assert resp.status_code == 303
        assert "/confirmation" in resp.headers["location"]
