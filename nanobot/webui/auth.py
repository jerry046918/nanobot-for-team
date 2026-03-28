"""Token generation and validation for WebUI authentication."""

import asyncio
import hashlib
import json
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import bcrypt
from loguru import logger

TOKENS_FILE = "webui_tokens.json"


class SessionManager:
    """Manages server-side sessions for authenticated users.

    Sessions are persisted to disk so they survive gateway restarts.
    """

    SESSIONS_FILE = "webui_sessions.json"

    def __init__(self, workspace: Path | None = None):
        self._sessions: dict[str, dict[str, Any]] = {}
        self._persist_path = workspace / self.SESSIONS_FILE if workspace else None
        self._lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        if not self._persist_path or not self._persist_path.exists():
            return
        try:
            data = json.loads(self._persist_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self._sessions = data
        except Exception:
            pass

    def _save(self) -> None:
        if not self._persist_path:
            return
        try:
            self._persist_path.write_text(
                json.dumps(self._sessions, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    def create_session(self, token_hash: str) -> str:
        """Create a new session and return session ID."""
        session_id = secrets.token_urlsafe(32)
        # Store hash of the token instead of raw value
        hashed = hashlib.sha256(token_hash.encode()).hexdigest()
        self._sessions[session_id] = {
            "token_hash": hashed,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """Check if session exists and is not expired."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        created = datetime.fromisoformat(session["created_at"])
        age = datetime.now(timezone.utc) - created
        return age < timedelta(hours=24)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session data."""
        return self._sessions.get(session_id)

    def destroy_session(self, session_id: str) -> bool:
        """Destroy a session. Returns True if existed."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save()
            return True
        return False

    def cleanup_expired(self, max_age_hours: int = 24) -> int:
        """Remove expired sessions. Returns count removed."""
        now = datetime.now(timezone.utc)
        expired = [
            sid for sid, s in self._sessions.items()
            if datetime.fromisoformat(s["created_at"]) + timedelta(hours=max_age_hours) < now
        ]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            self._save()
        return len(expired)


class TokenManager:
    """Manages WebUI authentication tokens."""

    def __init__(self, workspace: Path, ttl_hours: int = 24):
        self.workspace = workspace
        self.tokens_file = workspace / TOKENS_FILE
        self.ttl_hours = ttl_hours
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.tokens_file.exists():
            self.workspace.mkdir(parents=True, exist_ok=True)
            self._save_tokens([])

    def _load_tokens(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self.tokens_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_tokens(self, tokens: list[dict[str, Any]]) -> None:
        self.tokens_file.write_text(
            json.dumps(tokens, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def generate_token(self) -> str:
        """Generate a new token and store its hash."""
        token = secrets.token_urlsafe(24)[:32]
        token_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=self.ttl_hours)

        tokens = self._load_tokens()
        tokens.append({
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_used": now.isoformat(),
        })
        self._save_tokens(tokens)
        logger.info("Generated new WebUI token, expires at {}", expires_at)
        return token

    def validate_token(self, token: str) -> bool:
        """Validate a token against stored hashes."""
        if not token:
            return False

        tokens = self._load_tokens()
        now = datetime.now(timezone.utc)
        matched = False

        for t in tokens:
            expires_at = datetime.fromisoformat(t["expires_at"])
            if expires_at < now:
                continue
            if bcrypt.checkpw(token.encode(), t["token_hash"].encode()):
                matched = True
                t["last_used"] = now.isoformat()

        if matched:
            self._save_tokens(tokens)
        return matched

    def revoke_all(self) -> int:
        """Revoke all tokens. Returns count revoked."""
        tokens = self._load_tokens()
        count = len(tokens)
        self._save_tokens([])
        logger.info("Revoked all {} WebUI tokens", count)
        return count

    def cleanup_expired(self) -> int:
        """Remove expired tokens. Returns count removed."""
        tokens = self._load_tokens()
        now = datetime.now(timezone.utc)
        valid = [t for t in tokens if datetime.fromisoformat(t["expires_at"]) >= now]
        removed = len(tokens) - len(valid)
        if removed:
            self._save_tokens(valid)
            logger.info("Cleaned up {} expired tokens", removed)
        return removed
