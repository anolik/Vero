import hashlib
import json as json_module
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from config import ADMIN_USERNAME, ADMIN_PASSWORD, TOKEN_EXPIRY_DAYS, SECRET_KEY
from database import get_db

router = APIRouter(prefix="/admin")


def _make_session_token() -> str:
    return hashlib.sha256(f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}:{SECRET_KEY}".encode()).hexdigest()


class NotAuthenticated(Exception):
    pass


def verify_admin(request: Request) -> str:
    """Verify admin via session cookie."""
    token = request.cookies.get("admin_session")
    if token != _make_session_token():
        raise NotAuthenticated()
    return ADMIN_USERNAME


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return request.app.state.templates.TemplateResponse(
        request, "admin/login.html", {"error": error},
    )


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if secrets.compare_digest(username, ADMIN_USERNAME) and secrets.compare_digest(password, ADMIN_PASSWORD):
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie("admin_session", _make_session_token(), httponly=True, max_age=86400)
        return response
    return request.app.state.templates.TemplateResponse(
        request, "admin/login.html", {"error": "Identifiants invalides"}, status_code=401,
    )


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, username: str = Depends(verify_admin)):
    """Admin dashboard listing all sessions."""
    db = get_db()
    sessions = db.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    db.close()
    return request.app.state.templates.TemplateResponse(
        request, "admin/dashboard.html",
        {"sessions": sessions, "username": username},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_session_form(request: Request, username: str = Depends(verify_admin)):
    """Show the session creation form."""
    return request.app.state.templates.TemplateResponse(
        request, "admin/create_session.html", {},
    )


@router.post("/create")
async def create_session(
    request: Request,
    firm_name: str = Form(...),
    contact_name: str = Form(...),
    contact_email: str = Form(...),
    username: str = Depends(verify_admin),
):
    """Create a new session with a unique UUID4 token."""
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRY_DAYS)

    db = get_db()
    db.execute(
        """INSERT INTO sessions (token, firm_name, contact_name, contact_email, status, expires_at)
           VALUES (?, ?, ?, ?, 'pending', ?)""",
        (token, firm_name, contact_name, contact_email, expires_at.isoformat()),
    )
    db.commit()
    db.close()

    return RedirectResponse(url="/admin", status_code=303)


# ---------------------------------------------------------------------------
# F017: Session detail
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}", response_class=HTMLResponse)
async def session_detail(request: Request, session_id: int, username: str = Depends(verify_admin)):
    """Show all collected data for a session."""
    db = get_db()
    session = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not session:
        db.close()
        raise HTTPException(status_code=404, detail="Session introuvable")

    form_data = db.execute(
        "SELECT step, field_key, field_value FROM form_data WHERE session_id = ? ORDER BY step, field_key",
        (session_id,),
    ).fetchall()

    consent = db.execute(
        "SELECT * FROM consent_logs WHERE session_id = ?", (session_id,)
    ).fetchone()

    upload = db.execute(
        "SELECT * FROM uploads WHERE session_id = ? AND file_type = 'logo'", (session_id,)
    ).fetchone()

    db.close()

    data_by_step: dict[int, dict[str, str]] = {}
    for row in form_data:
        step = row["step"]
        if step not in data_by_step:
            data_by_step[step] = {}
        data_by_step[step][row["field_key"]] = row["field_value"]

    return request.app.state.templates.TemplateResponse(
        request, "admin/session_detail.html",
        {
            "session": session,
            "data_by_step": data_by_step,
            "consent": consent,
            "upload": upload,
        },
    )


# ---------------------------------------------------------------------------
# F012 + F019: JSON export
# ---------------------------------------------------------------------------

def _build_export_json(session_id: int) -> dict:
    """Build the structured JSON export for a session."""
    db = get_db()
    session = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not session:
        db.close()
        raise HTTPException(status_code=404, detail="Session introuvable")
    if session["status"] != "completed":
        db.close()
        raise HTTPException(status_code=400, detail="La session n'est pas encore completee")

    form_data = db.execute(
        "SELECT step, field_key, field_value FROM form_data WHERE session_id = ?",
        (session_id,),
    ).fetchall()

    consent = db.execute(
        "SELECT * FROM consent_logs WHERE session_id = ?", (session_id,)
    ).fetchone()

    upload = db.execute(
        "SELECT * FROM uploads WHERE session_id = ? AND file_type = 'logo'", (session_id,)
    ).fetchone()

    db.close()

    data: dict[str, str] = {}
    for row in form_data:
        data[row["field_key"]] = row["field_value"]

    variant_names = {1: "professionnel", 2: "chaleureux", 3: "concis"}

    # Look up actual variant numbers from template IDs
    template_ids = []
    categories = ["biography", "services", "client_approach", "credentials", "legal"]
    for cat in categories:
        tid = data.get(f"{cat}_template")
        if tid:
            template_ids.append(int(tid))

    variant_map = {}
    if template_ids:
        db2 = get_db()
        placeholders = ",".join("?" * len(template_ids))
        rows = db2.execute(
            f"SELECT id, variant FROM text_templates WHERE id IN ({placeholders})",
            template_ids,
        ).fetchall()
        db2.close()
        variant_map = {row["id"]: row["variant"] for row in rows}

    content = {}
    for cat in categories:
        tid = int(data.get(f"{cat}_template", "0"))
        variant = variant_map.get(tid, 1)
        content[cat] = {
            "category": cat,
            "selected_template": tid,
            "variant_name": variant_names.get(variant, "professionnel"),
            "final_text": data.get(f"{cat}_text", ""),
        }

    return {
        "meta": {
            "schema_version": "1.0",
            "session_id": session["token"],
            "firm_name": session["firm_name"],
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "status": session["status"],
        },
        "identity": {
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "email": data.get("email", ""),
            "firm_name": session["firm_name"],
        },
        "domain": {
            "has_existing": data.get("domain_option") == "existing",
            "existing_domain": data.get("domain_name") if data.get("domain_option") == "existing" else None,
            "requested_domain": data.get("domain_name") if data.get("domain_option") != "existing" else None,
        },
        "branding": {
            "logo_path": upload["storage_path"] if upload else None,
            "primary_color": data.get("primary_color", ""),
            "secondary_color": data.get("secondary_color", ""),
        },
        "content": content,
        "privacy": {
            "consent_given": bool(consent and consent["consent_given"]),
            "consent_timestamp": consent["consent_timestamp"] if consent else None,
            "data_purpose": "website_creation",
            "retention_policy": "2_years",
        },
    }


@router.get("/sessions/{session_id}/export")
async def export_json(session_id: int, username: str = Depends(verify_admin)):
    """Return structured JSON for the AI agent."""
    export = _build_export_json(session_id)
    return JSONResponse(content=export)


@router.get("/sessions/{session_id}/download")
async def download_json(session_id: int, username: str = Depends(verify_admin)):
    """Download JSON as a file."""
    export = _build_export_json(session_id)

    db = get_db()
    session = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    db.close()

    date_str = datetime.now().strftime("%Y%m%d")
    firm = session["firm_name"].replace(" ", "_")
    contact = session["contact_name"].replace(" ", "_")
    filename = f"{firm}_{contact}_{date_str}.json"

    return JSONResponse(
        content=export,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
