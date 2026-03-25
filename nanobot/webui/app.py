"""FastAPI application for WebUI."""

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.config.schema import Config
    from nanobot.team.manager import TeamManager

from nanobot.webui.auth import SessionManager, TokenManager


def create_app(
    bus: "MessageBus",
    agent: "AgentLoop",
    config: "Config",
    team_manager: "TeamManager | None",
) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="nanobot WebUI", docs_url=None, redoc_url=None)

    workspace = config.workspace_path
    app.state.bus = bus
    app.state.agent = agent
    app.state.config = config
    app.state.team_manager = team_manager
    app.state.workspace = workspace
    app.state.token_manager = TokenManager(workspace, config.webui.token_ttl_hours)
    app.state.session_manager = SessionManager()

    # Static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Templates
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    app.state.templates = templates

    # Register routes
    from nanobot.webui.routes import auth, chat, config as config_route, skills, team
    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(config_route.router)
    app.include_router(skills.router)
    app.include_router(team.router)

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, token: str = ""):
        """Landing page - handle token login or redirect to chat."""
        if token:
            # Validate token and create session
            if request.app.state.token_manager.validate_token(token):
                session_id = request.app.state.session_manager.create_session(token)
                response = templates.TemplateResponse(
                    "chat.html", {"request": request}
                )
                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    httponly=True,
                    max_age=86400,  # 24 hours
                )
                return response
            else:
                return templates.TemplateResponse(
                    "login.html", {"request": request, "error": "Invalid or expired token"}
                )

        # Check existing session
        session_id = request.cookies.get("session_id")
        if session_id and request.app.state.session_manager.validate_session(session_id):
            return templates.TemplateResponse("chat.html", {"request": request})

        return templates.TemplateResponse("login.html", {"request": request})

    @app.get("/api/health")
    async def health():
        return {"status": "healthy"}

    return app
