import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import ADMIN_USERNAME, ADMIN_PASSWORD, TOKEN_EXPIRY_DAYS
from database import get_db

router = APIRouter(prefix="/admin")
security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify admin credentials via HTTP Basic Auth."""
    if not secrets.compare_digest(credentials.username, ADMIN_USERNAME):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})
    if not secrets.compare_digest(credentials.password, ADMIN_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})
    return credentials.username


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
