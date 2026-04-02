from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

from database import get_db

router = APIRouter(prefix="/form")

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "svg"}
MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5 MB

CATEGORIES = ["biography", "services", "client_approach", "credentials", "legal"]
CATEGORY_LABELS = {
    "biography": "Biographie / A propos",
    "services": "Services offerts",
    "client_approach": "Approche client",
    "credentials": "Titres et accreditations",
    "legal": "Mentions legales",
}

TOTAL_STEPS = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_session_by_token(token: str) -> dict[str, Any] | None:
    """Retrieve a session by its unique token. Returns None if not found."""
    db = get_db()
    session = db.execute(
        "SELECT * FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    db.close()
    if session is None:
        return None
    return dict(session)


def validate_session(token: str) -> dict[str, Any]:
    """Validate a token and return the session dict, or raise HTTP errors."""
    session = get_session_by_token(token)
    if session is None:
        raise HTTPException(status_code=404, detail="Lien invalide")
    expires_at = datetime.fromisoformat(session["expires_at"])
    if datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=410, detail="Ce lien a expire")
    return session


def has_consent(session_id: int) -> bool:
    """Check whether a session already has consent logged."""
    db = get_db()
    row = db.execute(
        "SELECT consent_given FROM consent_logs WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    db.close()
    return row is not None and row["consent_given"] == 1


def get_form_data(session_id: int, step: int | None = None) -> dict[str, str]:
    """Return saved form data as a {field_key: field_value} dict.

    If *step* is provided, only return data for that step.
    """
    db = get_db()
    if step is not None:
        rows = db.execute(
            "SELECT field_key, field_value FROM form_data WHERE session_id = ? AND step = ?",
            (session_id, step),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT field_key, field_value FROM form_data WHERE session_id = ?",
            (session_id,),
        ).fetchall()
    db.close()
    return {row["field_key"]: row["field_value"] for row in rows}


def save_form_data(session_id: int, step: int, data_dict: dict[str, str]) -> None:
    """Upsert field_key/field_value pairs for a given session and step."""
    db = get_db()
    for key, value in data_dict.items():
        existing = db.execute(
            "SELECT id FROM form_data WHERE session_id = ? AND step = ? AND field_key = ?",
            (session_id, step, key),
        ).fetchone()
        if existing:
            db.execute(
                "UPDATE form_data SET field_value = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE session_id = ? AND step = ? AND field_key = ?",
                (value, session_id, step, key),
            )
        else:
            db.execute(
                "INSERT INTO form_data (session_id, step, field_key, field_value) VALUES (?, ?, ?, ?)",
                (session_id, step, key, value),
            )
    # Mark session as in_progress if still pending
    db.execute(
        "UPDATE sessions SET status = 'in_progress' WHERE id = ? AND status = 'pending'",
        (session_id,),
    )
    db.commit()
    db.close()


def get_completed_steps(session_id: int) -> set[int]:
    """Return the set of steps that have at least one saved field."""
    db = get_db()
    rows = db.execute(
        "SELECT DISTINCT step FROM form_data WHERE session_id = ?",
        (session_id,),
    ).fetchall()
    db.close()
    return {row["step"] for row in rows}


def get_last_incomplete_step(session_id: int) -> int:
    """Return the first step that hasn't been filled yet, or TOTAL_STEPS if all done."""
    completed = get_completed_steps(session_id)
    for s in range(1, TOTAL_STEPS + 1):
        if s not in completed:
            return s
    return TOTAL_STEPS


def hash_ip(ip: str) -> str:
    """SHA-256 hash of an IP address."""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def get_templates_by_category() -> dict[str, list[dict[str, Any]]]:
    """Load all text templates grouped by category."""
    db = get_db()
    rows = db.execute(
        "SELECT id, category, variant, title, content FROM text_templates ORDER BY category, variant"
    ).fetchall()
    db.close()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        cat = row["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(dict(row))
    return grouped


def get_upload_info(session_id: int, file_type: str = "logo") -> dict[str, Any] | None:
    """Retrieve upload record for a session."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM uploads WHERE session_id = ? AND file_type = ?",
        (session_id, file_type),
    ).fetchone()
    db.close()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# F006: Consent
# ---------------------------------------------------------------------------

@router.get("/{token}", response_class=HTMLResponse)
async def form_entry(request: Request, token: str) -> HTMLResponse:
    """Entry point for the representative form. Validates token."""
    session = validate_session(token)

    # If already consented, redirect to last incomplete step
    if has_consent(session["id"]):
        step = get_last_incomplete_step(session["id"])
        completed = get_completed_steps(session["id"])
        if len(completed) >= TOTAL_STEPS:
            return RedirectResponse(url=f"/form/{token}/confirmation", status_code=303)
        return RedirectResponse(url=f"/form/{token}/step/{step}", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request, "form/consent.html",
        {"session": session, "token": token},
    )


@router.post("/{token}/consent")
async def post_consent(request: Request, token: str, consent_given: str = Form(...)) -> RedirectResponse:
    """Save consent and redirect to step 1."""
    session = validate_session(token)

    if consent_given != "true":
        raise HTTPException(status_code=400, detail="Le consentement est requis")

    # Already consented? Skip to last incomplete step.
    if has_consent(session["id"]):
        step = get_last_incomplete_step(session["id"])
        return RedirectResponse(url=f"/form/{token}/step/{step}", status_code=303)

    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hash_ip(client_ip)

    db = get_db()
    db.execute(
        "INSERT INTO consent_logs (session_id, consent_given, consent_timestamp, consent_ip_hash) "
        "VALUES (?, 1, ?, ?)",
        (session["id"], datetime.now(timezone.utc).isoformat(), ip_hash),
    )
    db.commit()
    db.close()

    return RedirectResponse(url=f"/form/{token}/step/1", status_code=303)


# ---------------------------------------------------------------------------
# Middleware-like: require consent for all steps
# ---------------------------------------------------------------------------

def require_consent(session: dict[str, Any], token: str) -> None:
    """Raise redirect if consent not given."""
    if not has_consent(session["id"]):
        raise HTTPException(status_code=303, headers={"Location": f"/form/{token}"})


# ---------------------------------------------------------------------------
# F007: Step 1 — Text selection
# ---------------------------------------------------------------------------

@router.get("/{token}/step/1", response_class=HTMLResponse)
async def step1_get(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    templates_by_cat = get_templates_by_category()
    saved = get_form_data(session["id"], step=1)
    completed = get_completed_steps(session["id"])

    return request.app.state.templates.TemplateResponse(
        request, "form/step1_texts.html",
        {
            "token": token,
            "session": session,
            "categories": CATEGORIES,
            "category_labels": CATEGORY_LABELS,
            "templates_by_cat": templates_by_cat,
            "saved": saved,
            "current_step": 1,
            "completed_steps": completed,
            "total_steps": TOTAL_STEPS,
        },
    )


@router.post("/{token}/step/1")
async def step1_post(request: Request, token: str) -> RedirectResponse:
    session = validate_session(token)
    require_consent(session, token)

    form = await request.form()
    data: dict[str, str] = {}

    for cat in CATEGORIES:
        template_key = f"{cat}_template"
        text_key = f"{cat}_text"
        template_val = form.get(template_key, "")
        text_val = form.get(text_key, "")
        if template_val:
            data[template_key] = str(template_val)
        if text_val:
            data[text_key] = str(text_val)

    save_form_data(session["id"], step=1, data_dict=data)
    return RedirectResponse(url=f"/form/{token}/step/2", status_code=303)


# ---------------------------------------------------------------------------
# F008: Step 2 — Personal info
# ---------------------------------------------------------------------------

@router.get("/{token}/step/2", response_class=HTMLResponse)
async def step2_get(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    saved = get_form_data(session["id"], step=2)
    completed = get_completed_steps(session["id"])

    return request.app.state.templates.TemplateResponse(
        request, "form/step2_identity.html",
        {
            "token": token,
            "session": session,
            "saved": saved,
            "current_step": 2,
            "completed_steps": completed,
            "total_steps": TOTAL_STEPS,
        },
    )


@router.post("/{token}/step/2")
async def step2_post(
    request: Request,
    token: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
) -> RedirectResponse:
    session = validate_session(token)
    require_consent(session, token)

    data = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip(),
    }
    save_form_data(session["id"], step=2, data_dict=data)
    return RedirectResponse(url=f"/form/{token}/step/3", status_code=303)


# ---------------------------------------------------------------------------
# F009: Step 3 — Branding
# ---------------------------------------------------------------------------

@router.get("/{token}/step/3", response_class=HTMLResponse)
async def step3_get(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    saved = get_form_data(session["id"], step=3)
    completed = get_completed_steps(session["id"])
    upload = get_upload_info(session["id"], "logo")

    return request.app.state.templates.TemplateResponse(
        request, "form/step3_branding.html",
        {
            "token": token,
            "session": session,
            "saved": saved,
            "completed_steps": completed,
            "current_step": 3,
            "total_steps": TOTAL_STEPS,
            "existing_logo": upload,
        },
    )


@router.post("/{token}/step/3")
async def step3_post(
    request: Request,
    token: str,
    primary_color: str = Form(""),
    secondary_color: str = Form(""),
    logo: UploadFile | None = File(None),
) -> RedirectResponse:
    session = validate_session(token)
    require_consent(session, token)

    data: dict[str, str] = {}
    if primary_color:
        data["primary_color"] = primary_color.strip()
    if secondary_color:
        data["secondary_color"] = secondary_color.strip()

    # Handle logo upload
    if logo and logo.filename:
        ext = logo.filename.rsplit(".", 1)[-1].lower() if "." in logo.filename else ""
        if ext not in ALLOWED_LOGO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non accepte. Formats acceptes: {', '.join(ALLOWED_LOGO_EXTENSIONS)}",
            )

        contents = await logo.read()
        if len(contents) > MAX_LOGO_SIZE:
            raise HTTPException(status_code=400, detail="Le fichier depasse la taille maximale de 5 Mo")

        # Save file to uploads/{token}/
        upload_dir = UPLOADS_DIR / token
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"logo.{ext}"
        file_path = upload_dir / filename
        file_path.write_bytes(contents)

        storage_path = f"uploads/{token}/{filename}"
        data["logo_path"] = storage_path

        # Upsert in uploads table
        db = get_db()
        existing = db.execute(
            "SELECT id FROM uploads WHERE session_id = ? AND file_type = 'logo'",
            (session["id"],),
        ).fetchone()
        if existing:
            db.execute(
                "UPDATE uploads SET filename = ?, storage_path = ?, uploaded_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (filename, storage_path, existing["id"]),
            )
        else:
            db.execute(
                "INSERT INTO uploads (session_id, file_type, filename, storage_path) VALUES (?, 'logo', ?, ?)",
                (session["id"], filename, storage_path),
            )
        db.commit()
        db.close()

    save_form_data(session["id"], step=3, data_dict=data)
    return RedirectResponse(url=f"/form/{token}/step/4", status_code=303)


# ---------------------------------------------------------------------------
# F010: Step 4 — Domain
# ---------------------------------------------------------------------------

@router.get("/{token}/step/4", response_class=HTMLResponse)
async def step4_get(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    saved = get_form_data(session["id"], step=4)
    completed = get_completed_steps(session["id"])

    return request.app.state.templates.TemplateResponse(
        request, "form/step4_domain.html",
        {
            "token": token,
            "session": session,
            "saved": saved,
            "completed_steps": completed,
            "current_step": 4,
            "total_steps": TOTAL_STEPS,
        },
    )


@router.post("/{token}/step/4")
async def step4_post(
    request: Request,
    token: str,
    domain_option: str = Form(...),
    domain_name: str = Form(""),
) -> RedirectResponse:
    session = validate_session(token)
    require_consent(session, token)

    data = {
        "domain_option": domain_option.strip(),
    }
    if domain_name.strip():
        data["domain_name"] = domain_name.strip()

    save_form_data(session["id"], step=4, data_dict=data)
    return RedirectResponse(url=f"/form/{token}/confirmation", status_code=303)


# ---------------------------------------------------------------------------
# F011: Confirmation
# ---------------------------------------------------------------------------

@router.get("/{token}/confirmation", response_class=HTMLResponse)
async def confirmation_get(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    all_data = get_form_data(session["id"])
    completed = get_completed_steps(session["id"])
    upload = get_upload_info(session["id"], "logo")

    # Load template titles for display
    templates_by_cat = get_templates_by_category()

    return request.app.state.templates.TemplateResponse(
        request, "form/confirmation.html",
        {
            "token": token,
            "session": session,
            "data": all_data,
            "completed_steps": completed,
            "current_step": 5,
            "total_steps": TOTAL_STEPS,
            "existing_logo": upload,
            "categories": CATEGORIES,
            "category_labels": CATEGORY_LABELS,
            "templates_by_cat": templates_by_cat,
        },
    )


@router.post("/{token}/submit")
async def submit_form(request: Request, token: str) -> HTMLResponse:
    session = validate_session(token)
    require_consent(session, token)

    db = get_db()
    db.execute(
        "UPDATE sessions SET status = 'completed' WHERE id = ?",
        (session["id"],),
    )
    db.commit()
    db.close()

    return request.app.state.templates.TemplateResponse(
        request, "form/thank_you.html",
        {"token": token, "session": session},
    )
