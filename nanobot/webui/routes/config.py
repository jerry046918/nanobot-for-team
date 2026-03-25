"""Configuration routes for WebUI."""

import shutil
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["config"])


@router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request, session_id: str = Depends(require_auth)):
    return request.app.state.templates.TemplateResponse("config.html", {"request": request})


@router.get("/api/config")
async def get_config(request: Request, session_id: str = Depends(require_auth)):
    config = request.app.state.config
    return config.model_dump()


@router.put("/api/config")
async def save_config(
    request: Request,
    data: dict,
    session_id: str = Depends(require_auth)
):
    from nanobot.config.schema import Config
    from nanobot.config.loader import save_config

    # Validate
    try:
        validated = Config(**data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={
            "error": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": e.errors()
        })

    # Backup
    config_path = request.app.state.workspace / "config.json"
    if config_path.exists():
        shutil.copy(str(config_path), str(config_path) + ".bak")

    # Save
    save_config(validated, config_path)
    request.app.state.config = validated

    return {"status": "ok"}


@router.post("/api/config/validate")
async def validate_config(data: dict, session_id: str = Depends(require_auth)):
    from nanobot.config.schema import Config
    try:
        Config(**data)
        return {"valid": True}
    except ValidationError as e:
        return {"valid": False, "errors": e.errors()}


@router.post("/api/config/reload")
async def reload_config(request: Request, session_id: str = Depends(require_auth)):
    # Reload config from disk
    from nanobot.config.loader import load_config
    config_path = request.app.state.workspace / "config.json"
    request.app.state.config = load_config(config_path)
    return {"status": "ok"}
