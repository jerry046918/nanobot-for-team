"""Skills routes for WebUI."""

from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["skills"])

_MAX_ZIP_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_skill_name(name: str, workspace: Path) -> Path:
    """Validate skill name has no path traversal and stays within skills dir."""
    if not name or "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid skill name")
    skill_dir = (workspace / "skills" / name).resolve()
    skills_root = (workspace / "skills").resolve()
    if not str(skill_dir).startswith(str(skills_root)):
        raise HTTPException(status_code=400, detail="Path traversal detected")
    return skill_dir


@router.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request, session_id: str = Depends(require_auth)):
    return request.app.state.templates.TemplateResponse("skills.html", {"request": request})


@router.get("/api/skills")
async def list_skills(request: Request, session_id: str = Depends(require_auth)):
    from nanobot.agent.skills import SkillsLoader
    loader = SkillsLoader(request.app.state.workspace)
    return loader.list_skills(filter_unavailable=False)


@router.get("/api/skills/{name}")
async def get_skill(name: str, request: Request, session_id: str = Depends(require_auth)):
    from nanobot.agent.skills import SkillsLoader
    loader = SkillsLoader(request.app.state.workspace)
    content = loader.load_skill(name)
    if not content:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"name": name, "content": content}


@router.post("/api/skills")
async def create_skill(request: Request, data: dict, session_id: str = Depends(require_auth)):
    name = data.get("name")
    content = data.get("content", "")
    if not name:
        raise HTTPException(status_code=400, detail="Name required")

    skill_dir = _validate_skill_name(name, request.app.state.workspace)
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return {"status": "ok", "name": name}


@router.delete("/api/skills/{name}")
async def delete_skill(name: str, request: Request, session_id: str = Depends(require_auth)):
    import shutil
    skill_dir = _validate_skill_name(name, request.app.state.workspace)
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Skill not found")


@router.post("/api/skills/import/zip")
async def import_zip(
    request: Request,
    file: UploadFile = File(...),
    session_id: str = Depends(require_auth)
):
    import zipfile
    import io

    name = file.filename or "imported"
    if name.endswith(".zip"):
        name = name[:-4]

    content = await file.read()
    if len(content) > _MAX_ZIP_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    skill_dir = _validate_skill_name(name, request.app.state.workspace)
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_dir_resolved = skill_dir.resolve()

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for member in zf.namelist():
            # Security: prevent path traversal
            if member.startswith("/") or ".." in member:
                continue
            target = (skill_dir / member).resolve()
            if not str(target).startswith(str(skill_dir_resolved)):
                continue
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(member))

    return {"status": "ok", "name": name}
