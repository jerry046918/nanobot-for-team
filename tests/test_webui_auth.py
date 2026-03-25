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
