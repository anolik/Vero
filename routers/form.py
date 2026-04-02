from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

from database import get_db

router = APIRouter(prefix="/form")


def get_session_by_token(token: str):
    """Retrieve a session by its unique token. Returns None if not found."""
    db = get_db()
    session = db.execute(
        "SELECT * FROM sessions WHERE token = ?", (token,)
    ).fetchone()
    db.close()
    return session


@router.get("/{token}", response_class=HTMLResponse)
async def form_entry(request: Request, token: str):
    """Entry point for the representative form. Validates token."""
    session = get_session_by_token(token)
    if session is None:
        raise HTTPException(status_code=404, detail="Lien invalide")

    expires_at = datetime.fromisoformat(session["expires_at"])
    if datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=410, detail="Ce lien a expiré")

    return request.app.state.templates.TemplateResponse(
        request, "form/consent.html",
        {"session": session, "token": token},
    )
