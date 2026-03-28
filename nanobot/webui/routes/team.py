"""Team routes for WebUI."""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["team"])


def _get_team_manager(request: Request):
    """Get or lazily create a TeamManager when team mode is enabled."""
    tm = request.app.state.team_manager
    if tm is not None:
        return tm

    # Check if team mode is enabled in the current config
    config = request.app.state.config
    if config.team.enabled:
        from nanobot.team.manager import TeamManager
        tm = TeamManager(request.app.state.workspace)
        request.app.state.team_manager = tm
        return tm

    return None


@router.get("/team", response_class=HTMLResponse)
async def team_page(request: Request, session_id: str = Depends(require_auth)):
    return request.app.state.templates.TemplateResponse("team.html", {"request": request})


@router.get("/api/team/status")
async def team_status(request: Request, session_id: str = Depends(require_auth)):
    """Check if team mode is enabled and return status."""
    config = request.app.state.config
    tm = _get_team_manager(request)
    return {
        "enabled": config.team.enabled,
        "member_count": len(tm.list_members()) if tm else 0,
    }


@router.get("/api/team/members")
async def list_members(request: Request, session_id: str = Depends(require_auth)):
    tm = _get_team_manager(request)
    if not tm:
        return []
    return [
        {
            "nickname": m.nickname,
            "role": m.role,
            "channel_ids": m.channel_ids,
            "joined_at": m.joined_at,
            "invited_by": m.invited_by,
        }
        for m in tm.list_members()
    ]


@router.post("/api/team/members")
async def add_member(
    request: Request,
    data: dict,
    session_id: str = Depends(require_auth)
):
    tm = _get_team_manager(request)
    if not tm:
        raise HTTPException(status_code=400, detail="Team mode not enabled")

    try:
        member = tm.add_member(
            nickname=data["nickname"],
            channel=data.get("channel", "webui"),
            sender_id=data.get("sender_id", "admin"),
            role=data.get("role", "member"),
            invited_by="webui",
        )
        return {"status": "ok", "nickname": member.nickname}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/team/members/{nickname}")
async def update_member(
    nickname: str,
    request: Request,
    data: dict,
    session_id: str = Depends(require_auth)
):
    tm = _get_team_manager(request)
    if not tm:
        raise HTTPException(status_code=400, detail="Team mode not enabled")

    member = tm.get_member_by_nickname(nickname)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if "role" in data:
        tm.set_role(nickname, data["role"])
    if "channel_ids" in data:
        for channel, sender_id in data["channel_ids"].items():
            tm.bind_channel(nickname, channel, sender_id)

    return {"status": "ok"}


@router.delete("/api/team/members/{nickname}")
async def remove_member(
    nickname: str,
    request: Request,
    session_id: str = Depends(require_auth)
):
    tm = _get_team_manager(request)
    if not tm:
        raise HTTPException(status_code=400, detail="Team mode not enabled")

    if tm.remove_member(nickname):
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Member not found")
