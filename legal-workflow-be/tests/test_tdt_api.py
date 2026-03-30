"""Step 6: TDT + TDTP Config CRUD API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Clean repositories before each test."""
    from src.modules.tdt.repository import tdt_repository
    from src.modules.tdtp.repository import tdtp_repository
    tdt_repository.clear()
    tdtp_repository.clear()
    yield
    tdt_repository.clear()
    tdtp_repository.clear()


class TestTDTListAPI:
    """Test GET /api/legal/config/tdt."""

    @pytest.mark.asyncio
    async def test_get_tdt_returns_list(self, client):
        """GET /tdt returns list."""
        token = make_token(role="ADMIN")
        # Create a TDT first
        await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={"tdt_code": "DOC001", "tdt_name": "Screenshot Document"},
        )
        response = await client.get(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1


class TestTDTCreateAPI:
    """Test POST /api/legal/config/tdt."""

    @pytest.mark.asyncio
    async def test_create_tdt(self, client):
        """POST /tdt creates."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={
                "tdt_code": "DOC001",
                "tdt_name": "Screenshot Document",
                "file_extensions": ".png,.jpg",
                "max_file_size_mb": 10,
                "is_required": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["tdt_code"] == "DOC001"
        assert data["data"]["tdt_id"].startswith("TDT-")
        assert data["data"]["is_required"] is True


class TestTDTPCreateAPI:
    """Test POST /api/legal/config/tdtp."""

    @pytest.mark.asyncio
    async def test_create_tdtp_linked_to_tdt(self, client):
        """POST /tdtp with tdt_id creates and links."""
        token = make_token(role="ADMIN")
        # Create a TDT first
        tdt_resp = await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={"tdt_code": "DOC001", "tdt_name": "Screenshot Doc"},
        )
        tdt_id = tdt_resp.json()["data"]["tdt_id"]

        # Create TDTP linked to TDT
        response = await client.post(
            "/api/legal/config/tdtp/",
            headers=auth_header(token),
            json={
                "tdt_id": tdt_id,
                "tdtp_code": "TPL001",
                "tdtp_name": "Screenshot Template",
                "template_structure": {"fields": ["screenshot_url", "description"]},
                "sample_data": {"screenshot_url": "https://example.com/img.png"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["tdt_id"] == tdt_id
        assert data["data"]["tdtp_id"].startswith("TDTP-")
        assert data["data"]["template_structure"]["fields"] == ["screenshot_url", "description"]

    @pytest.mark.asyncio
    async def test_create_tdtp_duplicate_tdt_returns_400(self, client):
        """POST /tdtp with already-linked tdt_id returns 400."""
        token = make_token(role="ADMIN")
        # Create TDT
        tdt_resp = await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={"tdt_code": "DOC002", "tdt_name": "Report Doc"},
        )
        tdt_id = tdt_resp.json()["data"]["tdt_id"]

        # First TDTP
        await client.post(
            "/api/legal/config/tdtp/",
            headers=auth_header(token),
            json={
                "tdt_id": tdt_id,
                "tdtp_code": "TPL002",
                "tdtp_name": "Report Template",
            },
        )

        # Second TDTP for same TDT → 400
        response = await client.post(
            "/api/legal/config/tdtp/",
            headers=auth_header(token),
            json={
                "tdt_id": tdt_id,
                "tdtp_code": "TPL003",
                "tdtp_name": "Duplicate Template",
            },
        )
        assert response.status_code == 400
        assert "already has a template" in response.json()["message"]
