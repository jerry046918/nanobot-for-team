"""Chat routes for WebUI."""

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from loguru import logger

from nanobot.webui.routes.auth import require_auth

router = APIRouter(tags=["chat"])


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str = Depends(require_auth)):
    return request.app.state.templates.TemplateResponse(
        "chat.html", {"request": request, "ws_session_id": session_id}
    )


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
    # Check Origin header for security
    # Normalize ws->http and wss->https for comparison, since browser sends
    # http/https but websocket.url.scheme is ws/wss
    origin = websocket.headers.get("origin")
    host = websocket.headers.get("host", "")
    scheme = websocket.url.scheme.replace("ws", "http", 1)
    expected_origin = f"{scheme}://{host}"
    if origin and origin != expected_origin:
        await websocket.close(code=4003, reason="Invalid Origin")
        return

    await websocket.accept()
    # Validate session from query param
    session_id = websocket.query_params.get("session_id")
    if not session_id or not websocket.app.state.session_manager.validate_session(session_id):
        await websocket.close(code=4001, reason="Unauthorized")
        return

    agent = websocket.app.state.agent
    processing = False

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            if not message.strip():
                continue

            if processing:
                await websocket.send_json({
                    "type": "error",
                    "content": "Still processing previous message, please wait.",
                })
                continue

            processing = True
            try:
                # Callbacks for streaming and progress
                async def on_stream(delta: str) -> None:
                    await websocket.send_json({"type": "stream", "content": delta})

                async def on_stream_end(*, resuming: bool = False) -> None:
                    await websocket.send_json({
                        "type": "stream_end",
                        "resuming": resuming,
                    })

                async def on_progress(content: str, **kwargs) -> None:
                    tool_hint = kwargs.get("tool_hint", False)
                    await websocket.send_json({
                        "type": "progress",
                        "content": content,
                        "tool_hint": tool_hint,
                    })

                response = await agent.process_direct(
                    content=message,
                    session_key="webui:direct",
                    channel="webui",
                    chat_id="direct",
                    on_progress=on_progress,
                    on_stream=on_stream,
                    on_stream_end=on_stream_end,
                )

                if response and response.content:
                    await websocket.send_json({"type": "text", "content": response.content})
                elif response is None:
                    await websocket.send_json({"type": "text", "content": ""})

            except Exception as e:
                logger.exception("WebUI chat error")
                await websocket.send_json({"type": "error", "content": f"Error: {e}"})
            finally:
                processing = False

    except WebSocketDisconnect:
        pass
