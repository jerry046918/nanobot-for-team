# tests/test_webui_integration.py
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from nanobot.config.schema import Config
from nanobot.webui.app import create_app
from nanobot.bus.queue import MessageBus


@pytest.fixture
def test_client(tmp_path):
    config = Config()
    config.agents.defaults.workspace = str(tmp_path)

    bus = MessageBus()
    app = create_app(bus, None, config, None)
    return TestClient(app)


def test_health_endpoint(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_page_without_token(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "login" in response.text.lower() or "webui" in response.text.lower()


def test_login_with_invalid_token(test_client):
    response = test_client.get("/?token=invalidtoken12345678901234567890")
    assert response.status_code == 200
    # Should show login page with error
