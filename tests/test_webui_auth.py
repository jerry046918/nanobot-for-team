"""Tests for nanobot.webui.auth module."""

import pytest
from pathlib import Path
from nanobot.webui.auth import TokenManager


def test_generate_token(tmp_path):
    """Test token generation produces valid 32-character tokens."""
    tm = TokenManager(tmp_path)
    token = tm.generate_token()
    assert len(token) == 32
    assert tm.validate_token(token) is True


def test_invalid_token(tmp_path):
    """Test that invalid tokens are rejected."""
    tm = TokenManager(tmp_path)
    assert tm.validate_token("invalid") is False
    assert tm.validate_token("") is False
    assert tm.validate_token("a" * 31) is False
    assert tm.validate_token("a" * 33) is False


def test_expired_token(tmp_path):
    """Test that expired tokens are rejected."""
    tm = TokenManager(tmp_path, ttl_hours=0)
    token = tm.generate_token()
    assert tm.validate_token(token) is False  # immediately expired


def test_revoke_all(tmp_path):
    """Test revoking all tokens."""
    tm = TokenManager(tmp_path)
    token1 = tm.generate_token()
    token2 = tm.generate_token()

    assert tm.validate_token(token1) is True
    assert tm.validate_token(token2) is True

    count = tm.revoke_all()
    assert count == 2
    assert tm.validate_token(token1) is False
    assert tm.validate_token(token2) is False


def test_cleanup_expired(tmp_path):
    """Test cleanup of expired tokens."""
    tm = TokenManager(tmp_path, ttl_hours=0)
    tm.generate_token()
    tm.generate_token()

    removed = tm.cleanup_expired()
    assert removed == 2


def test_multiple_tokens(tmp_path):
    """Test managing multiple tokens."""
    tm = TokenManager(tmp_path)
    tokens = [tm.generate_token() for _ in range(5)]

    for token in tokens:
        assert tm.validate_token(token) is True

    # Invalid token should not validate
    assert tm.validate_token("x" * 32) is False


def test_token_persistence(tmp_path):
    """Test that tokens persist across TokenManager instances."""
    tm1 = TokenManager(tmp_path)
    token = tm1.generate_token()

    tm2 = TokenManager(tmp_path)
    assert tm2.validate_token(token) is True


def test_session_manager():
    from nanobot.webui.auth import SessionManager
    sm = SessionManager()
    session_id = sm.create_session("test_token_hash")
    assert sm.validate_session(session_id) is True
    sm.destroy_session(session_id)
    assert sm.validate_session(session_id) is False


def test_expired_session():
    """Test that expired sessions are rejected."""
    from nanobot.webui.auth import SessionManager
    from datetime import datetime, timezone, timedelta

    sm = SessionManager()
    # Manually create an old session
    import uuid
    old_session_id = str(uuid.uuid4())
    sm._sessions[old_session_id] = {
        "token_hash": "test_hash",
        "created_at": (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    }

    # Session should be expired
    assert sm.validate_session(old_session_id) is False

    # Fresh session should still work
    session_id = sm.create_session("test_token_hash")
    assert sm.validate_session(session_id) is True


def test_get_session_invalid():
    """Test that get_session returns None for invalid session."""
    from nanobot.webui.auth import SessionManager

    sm = SessionManager()
    assert sm.get_session("invalid_session") is None
    assert sm.get_session("") is None

    # Valid session should return session data
    session_id = sm.create_session("test_token_hash")
    session_data = sm.get_session(session_id)
    assert session_data is not None
    # token_hash is now SHA-256 hashed, not stored raw
    import hashlib
    expected_hash = hashlib.sha256("test_token_hash".encode()).hexdigest()
    assert session_data["token_hash"] == expected_hash


def test_cleanup_expired():
    """Test cleanup of expired sessions."""
    from nanobot.webui.auth import SessionManager
    from datetime import datetime, timezone, timedelta
    import uuid

    sm = SessionManager()

    # Create fresh session
    fresh_session = sm.create_session("fresh_token")

    # Manually create old session
    old_session_id = str(uuid.uuid4())
    sm._sessions[old_session_id] = {
        "token_hash": "old_token",
        "created_at": (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    }

    # Count before cleanup
    assert len(sm._sessions) == 2

    # Cleanup expired sessions
    removed = sm.cleanup_expired()
    assert removed == 1
    assert len(sm._sessions) == 1

    # Fresh session should still exist
    assert sm.validate_session(fresh_session) is True

    # Old session should be gone
    assert sm.validate_session(old_session_id) is False
