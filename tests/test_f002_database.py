"""F002: Tests for database schema and seed data (includes F013 text templates)."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, get_db


@pytest.fixture
def db(tmp_path):
    """Create an initialized temporary database."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = get_db(db_path)
    yield conn
    conn.close()


# ── Schema tests ──

def test_sessions_table_columns(db):
    """Sessions table should have all required columns."""
    cols = db.execute("PRAGMA table_info(sessions)").fetchall()
    col_names = [c["name"] for c in cols]
    assert "id" in col_names
    assert "token" in col_names
    assert "firm_name" in col_names
    assert "contact_name" in col_names
    assert "contact_email" in col_names
    assert "status" in col_names
    assert "expires_at" in col_names
    assert "created_at" in col_names


def test_form_data_table_columns(db):
    """form_data table should have all required columns."""
    cols = db.execute("PRAGMA table_info(form_data)").fetchall()
    col_names = [c["name"] for c in cols]
    assert "session_id" in col_names
    assert "step" in col_names
    assert "field_key" in col_names
    assert "field_value" in col_names


def test_uploads_table_columns(db):
    """uploads table should have all required columns."""
    cols = db.execute("PRAGMA table_info(uploads)").fetchall()
    col_names = [c["name"] for c in cols]
    assert "session_id" in col_names
    assert "file_type" in col_names
    assert "filename" in col_names
    assert "storage_path" in col_names


def test_consent_logs_table_columns(db):
    """consent_logs table should have all required columns."""
    cols = db.execute("PRAGMA table_info(consent_logs)").fetchall()
    col_names = [c["name"] for c in cols]
    assert "session_id" in col_names
    assert "consent_given" in col_names
    assert "consent_timestamp" in col_names
    assert "consent_ip_hash" in col_names


def test_text_templates_table_columns(db):
    """text_templates table should have all required columns."""
    cols = db.execute("PRAGMA table_info(text_templates)").fetchall()
    col_names = [c["name"] for c in cols]
    assert "category" in col_names
    assert "variant" in col_names
    assert "title" in col_names
    assert "content" in col_names


def test_foreign_key_constraint_form_data(db):
    """form_data FK should prevent orphaned records."""
    with pytest.raises(Exception):
        db.execute(
            "INSERT INTO form_data (session_id, step, field_key, field_value) VALUES (9999, 1, 'key', 'val')"
        )


def test_foreign_key_constraint_consent_logs(db):
    """consent_logs FK should prevent orphaned records."""
    with pytest.raises(Exception):
        db.execute(
            "INSERT INTO consent_logs (session_id, consent_given) VALUES (9999, 1)"
        )


def test_variant_check_constraint(db):
    """text_templates variant must be between 1 and 3."""
    with pytest.raises(Exception):
        db.execute(
            "INSERT INTO text_templates (category, variant, title, content) VALUES ('test', 4, 'Test', 'Content')"
        )


# ── Seed data tests (F013) ──

def test_seed_data_count(db):
    """Should have exactly 15 text templates (5 categories x 3 variants)."""
    count = db.execute("SELECT COUNT(*) FROM text_templates").fetchone()[0]
    assert count == 15


def test_seed_data_categories(db):
    """Should have exactly 5 categories."""
    categories = db.execute(
        "SELECT DISTINCT category FROM text_templates ORDER BY category"
    ).fetchall()
    cat_names = [c["category"] for c in categories]
    assert len(cat_names) == 5
    assert "biography" in cat_names
    assert "services" in cat_names
    assert "client_approach" in cat_names
    assert "credentials" in cat_names
    assert "legal" in cat_names


def test_seed_data_three_variants_per_category(db):
    """Each category should have exactly 3 variants."""
    for category in ["biography", "services", "client_approach", "credentials", "legal"]:
        count = db.execute(
            "SELECT COUNT(*) FROM text_templates WHERE category = ?", (category,)
        ).fetchone()[0]
        assert count == 3, f"{category} should have 3 variants, got {count}"


def test_seed_data_variants_are_1_2_3(db):
    """Each category should have variants 1, 2, and 3."""
    for category in ["biography", "services", "client_approach", "credentials", "legal"]:
        variants = db.execute(
            "SELECT variant FROM text_templates WHERE category = ? ORDER BY variant",
            (category,),
        ).fetchall()
        assert [v["variant"] for v in variants] == [1, 2, 3]


def test_seed_data_content_mentions_financial_products(db):
    """Services texts should mention fonds communs and assurance."""
    services = db.execute(
        "SELECT content FROM text_templates WHERE category = 'services'"
    ).fetchall()
    all_content = " ".join(s["content"] for s in services).lower()
    assert "fonds communs" in all_content
    assert "assurance" in all_content


def test_seed_data_idempotent(tmp_path):
    """Running init_db twice should not duplicate seed data."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    init_db(db_path)  # second call
    conn = get_db(db_path)
    count = conn.execute("SELECT COUNT(*) FROM text_templates").fetchone()[0]
    conn.close()
    assert count == 15


def test_seed_data_legal_mentions_amf(db):
    """Legal texts should mention AMF (Autorité des marchés financiers)."""
    legal = db.execute(
        "SELECT content FROM text_templates WHERE category = 'legal'"
    ).fetchall()
    all_content = " ".join(l["content"] for l in legal).lower()
    assert "amf" in all_content or "autorité des marchés financiers" in all_content
