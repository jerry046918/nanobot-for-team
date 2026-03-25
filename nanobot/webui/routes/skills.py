"""Skills routes for WebUI."""

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["skills"])


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

    skill_dir = request.app.state.workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return {"status": "ok", "name": name}


@router.delete("/api/skills/{name}")
async def delete_skill(name: str, request: Request, session_id: str = Depends(require_auth)):
    import shutil
    skill_dir = request.app.state.workspace / "skills" / name
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
    skill_dir = request.app.state.workspace / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for member in zf.namelist():
            # Security: prevent path traversal
            if member.startswith("/") or ".." in member:
                continue
            target = skill_dir / member
            if member.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(member))

    return {"status": "ok", "name": name}
