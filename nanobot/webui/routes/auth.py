"""Authentication routes for WebUI."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_session_manager(request: Request):
    return request.app.state.session_manager


def require_auth(request: Request):
    """Dependency that requires valid session."""
    session_id = request.cookies.get("session_id")
    if not session_id or not request.app.state.session_manager.validate_session(session_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")
    return session_id


@router.post("/logout")
async def logout(request: Request):
    """Logout current session."""
    session_id = request.cookies.get("session_id")
    if session_id:
        request.app.state.session_manager.destroy_session(session_id)
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response
