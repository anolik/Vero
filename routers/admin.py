import secrets
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import ADMIN_USERNAME, ADMIN_PASSWORD
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
