import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

client = TestClient(app)

# We need to mock get_current_user to bypass auth
def mock_get_current_user():
    class MockUser:
        id = "mock_user_id"
        tenant_id = "mock_tenant_id"
    return MockUser()

app.dependency_overrides["src.core.auth.get_current_user"] = mock_get_current_user

def test_settings_get_hides_api_key():
    # Setup mock DB
    with patch("src.api.settings.get_db") as mock_db_dep:
        mock_db = MagicMock()
        mock_db_dep.return_value = mock_db
        
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.llm_api_key = "some_encrypted_key"
        mock_db.query().filter().first.return_value = mock_settings
        
        # We also need to override get_db dependency for the route
        app.dependency_overrides["src.core.database.get_db"] = lambda: mock_db
        
        res = client.get("/settings")
        assert res.status_code == 200
        data = res.json()
        assert data["has_byok_key"] is True
        assert "gemini_api_key" not in data
        assert "supported_gemini_models" in data

def test_llm_test_hides_raw_exception():
    with patch("src.api.settings.client.complete", side_effect=Exception("SUPER SECRET RAW EXCEPTION")):
        mock_db = MagicMock()
        app.dependency_overrides["src.core.database.get_db"] = lambda: mock_db
        
        res = client.post("/settings/test-llm")
        assert res.status_code == 502
        assert "SUPER SECRET" not in res.json()["detail"]
        assert "Unable to connect" in res.json()["detail"]

def test_clear_data_unauthorized():
    mock_db = MagicMock()
    # Return None for the ProjectMember admin check
    mock_db.query().filter().first.return_value = None
    app.dependency_overrides["src.core.database.get_db"] = lambda: mock_db
    
    res = client.post("/settings/clear-data", json={"confirmation": "DELETE ALL DATA"})
    assert res.status_code == 403
    assert "OWNER or ADMIN" in res.json()["detail"]
