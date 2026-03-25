"""Token generation and validation for WebUI authentication."""

import json
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import bcrypt
from loguru import logger

TOKENS_FILE = "webui_tokens.json"


class SessionManager:
    """Manages server-side sessions for authenticated users."""

    def __init__(self):
        self._sessions: dict[str, dict[str, Any]] = {}

    def create_session(self, token_hash: str) -> str:
        """Create a new session and return session ID."""
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            "token_hash": token_hash,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
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
        if not token or len(token) != 32:
            return False

        tokens = self._load_tokens()
        now = datetime.now(timezone.utc)

        for t in tokens:
            expires_at = datetime.fromisoformat(t["expires_at"])
            if expires_at < now:
                continue
            if bcrypt.checkpw(token.encode(), t["token_hash"].encode()):
                t["last_used"] = now.isoformat()
                self._save_tokens(tokens)
                return True
        return False

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
