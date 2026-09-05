import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.core.auth import get_current_user
from src.core.database import get_db

client = TestClient(app)

# We need to mock get_current_user to bypass auth
def mock_get_current_user():
    class MockUser:
        id = "mock_user_id"
        tenant_id = "mock_tenant_id"
    return MockUser()

app.dependency_overrides[get_current_user] = mock_get_current_user

# Mock CSRF middleware by passing it through via cookie/header matching
@pytest.fixture(autouse=True)
def set_csrf_cookie(monkeypatch):
    client.cookies.set("csrf_token", "test_csrf_token")
    client.headers.update({"x-csrf-token": "test_csrf_token"})

def test_settings_get_hides_api_key():
    mock_db = MagicMock()
    mock_settings = MagicMock()
    mock_settings.llm_api_key = "some_encrypted_key"
    mock_db.query().filter().first.return_value = mock_settings
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    res = client.get("/settings")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["has_byok_key"] is True
    assert "gemini_api_key" not in data
    assert "supported_gemini_models" in data

def test_llm_test_hides_raw_exception():
    with patch("src.api.settings.client.complete", side_effect=Exception("SUPER SECRET RAW EXCEPTION")):
        mock_db = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        
        res = client.post("/settings/test-llm")
        assert res.status_code == 502, res.text
        assert "SUPER SECRET" not in res.json()["detail"]
        assert "Unable to connect" in res.json()["detail"]

def test_clear_data_unauthorized():
    mock_db = MagicMock()
    # Return None for the ProjectMember admin check
    mock_db.query().filter().first.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db
    
    res = client.post("/settings/clear-data", json={"confirmation": "DELETE ALL DATA"})
    assert res.status_code == 403, res.text
    assert "OWNER or ADMIN" in res.json()["detail"]
