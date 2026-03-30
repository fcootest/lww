"""Step 0: Health endpoint and app startup tests."""

import pytest


class TestHealthEndpoint:
    """Test GET /api/health returns correct response."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        """Health endpoint returns 200 OK."""
        response = await client.get("/api/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_returns_success_true(self, client):
        """Health response has success=true."""
        response = await client.get("/api/health")
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_health_returns_message_ok(self, client):
        """Health response message is 'OK'."""
        response = await client.get("/api/health")
        data = response.json()
        assert data["message"] == "OK"

    @pytest.mark.asyncio
    async def test_health_returns_version(self, client):
        """Health response includes version in data."""
        response = await client.get("/api/health")
        data = response.json()
        assert "version" in data["data"]
        assert data["data"]["version"] == "0.1.0"


class TestAppStartup:
    """Test that the application starts without import errors."""

    def test_app_can_be_imported(self):
        """FastAPI app imports without errors."""
        from src.app import app
        assert app is not None

    def test_app_has_title(self):
        """App has correct title."""
        from src.app import app
        assert app.title == "Legal Workflow API"

    def test_settings_can_be_imported(self):
        """Settings load without errors."""
        from src.config.settings import settings
        assert settings.APP_NAME == "Legal Workflow API"
        assert settings.BQ_PROJECT_ID == "fp-a-project"
        assert settings.BQ_DATASET == "legal_workflow"


class TestResponseUtils:
    """Test common response utilities."""

    def test_send_success_format(self):
        """send_success returns correct JSON structure."""
        from src.common.response import send_success
        resp = send_success(data={"key": "value"}, message="Test OK")
        body = resp.body.decode()
        import json
        parsed = json.loads(body)
        assert parsed["success"] is True
        assert parsed["data"]["key"] == "value"
        assert parsed["message"] == "Test OK"

    def test_send_success_default_status(self):
        """send_success defaults to 200."""
        from src.common.response import send_success
        resp = send_success()
        assert resp.status_code == 200

    def test_send_error_format(self):
        """send_error returns correct JSON structure."""
        from src.common.response import send_error
        resp = send_error(message="Not Found", status_code=404)
        body = resp.body.decode()
        import json
        parsed = json.loads(body)
        assert parsed["success"] is False
        assert parsed["message"] == "Not Found"
        assert resp.status_code == 404

    def test_send_success_with_201(self):
        """send_success can return 201."""
        from src.common.response import send_success
        resp = send_success(data={"id": "123"}, message="Created", status_code=201)
        assert resp.status_code == 201
