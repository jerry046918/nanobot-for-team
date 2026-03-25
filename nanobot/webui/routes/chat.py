"""Chat routes for WebUI."""

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from typing import Any

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["chat"])


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str = Depends(require_auth)):
    return request.app.state.templates.TemplateResponse("chat.html", {"request": request})


@router.get("/api/sessions")
async def list_sessions(request: Request, session_id: str = Depends(require_auth)):
    """List all conversation sessions."""
    sessions = request.app.state.agent.sessions.list_sessions()
    return sessions


@router.get("/api/sessions/{key}/history")
async def get_history(key: str, request: Request, session_id: str = Depends(require_auth)):
    """Get message history for a specific session."""
    session = request.app.state.agent.sessions.get_or_create(key)
    return session.get_history()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    await websocket.accept()
    # Validate session from query param or cookie
    session_id = websocket.query_params.get("session_id")
    if not session_id or not websocket.app.state.session_manager.validate_session(session_id):
        await websocket.close(code=4001, reason="Unauthorized")
        return

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            # Send to agent via bus
            from nanobot.bus.events import InboundMessage
            msg = InboundMessage(
                channel="webui",
                sender_id="admin",
                chat_id="direct",
                content=message,
            )
            await websocket.app.state.bus.publish_inbound(msg)

            # For now, just echo - real implementation would stream response
            await websocket.send_json({"type": "text", "content": f"Received: {message}"})
    except WebSocketDisconnect:
        pass
