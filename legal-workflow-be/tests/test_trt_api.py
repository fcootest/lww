"""Step 7: TRT + TST_TRT Config CRUD API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Clean repositories before each test."""
    from src.modules.tst.repository import tst_repository
    from src.modules.trt.repository import trt_repository, tst_trt_repository
    from src.seeds.seed_tst import ALL_SEED

    tst_repository.clear()
    tst_repository.seed(ALL_SEED)
    trt_repository.clear()
    tst_trt_repository.clear()
    yield
    tst_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()


class TestTRTListAPI:
    """Test GET /api/legal/config/trt."""

    @pytest.mark.asyncio
    async def test_get_returns_roles(self, client):
        """GET returns roles."""
        token = make_token(role="ADMIN")
        # Create a role first
        await client.post(
            "/api/legal/config/trt",
            headers=auth_header(token),
            json={"trt_code": "REVIEWER", "trt_name": "Legal Reviewer"},
        )
        response = await client.get(
            "/api/legal/config/trt",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1


class TestTRTCreateAPI:
    """Test POST /api/legal/config/trt."""

    @pytest.mark.asyncio
    async def test_create_role(self, client):
        """POST creates role."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/trt",
            headers=auth_header(token),
            json={
                "trt_code": "APPROVER",
                "trt_name": "Legal Approver",
                "description": "Can approve legal reviews",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["trt_code"] == "APPROVER"
        assert data["data"]["trt_id"].startswith("TRT-")


class TestTSTTRTMappingAPI:
    """Test POST /api/legal/config/tst-trt."""

    @pytest.mark.asyncio
    async def test_map_role_to_tst(self, client):
        """POST /tst-trt maps role."""
        token = make_token(role="ADMIN")
        # Create a role
        trt_resp = await client.post(
            "/api/legal/config/trt",
            headers=auth_header(token),
            json={"trt_code": "CHECKER", "trt_name": "Copyright Checker"},
        )
        trt_id = trt_resp.json()["data"]["trt_id"]

        # Map to TST
        response = await client.post(
            "/api/legal/config/tst-trt",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "trt_id": trt_id,
                "is_required": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["tst_id"] == "TST-001"
        assert data["data"]["trt_id"] == trt_id
        assert data["data"]["is_required"] is True

    @pytest.mark.asyncio
    async def test_duplicate_mapping_returns_400(self, client):
        """Duplicate mapping returns 400."""
        token = make_token(role="ADMIN")
        # Create a role
        trt_resp = await client.post(
            "/api/legal/config/trt",
            headers=auth_header(token),
            json={"trt_code": "DUP_ROLE", "trt_name": "Duplicate Test Role"},
        )
        trt_id = trt_resp.json()["data"]["trt_id"]

        # First mapping
        await client.post(
            "/api/legal/config/tst-trt",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "trt_id": trt_id},
        )

        # Duplicate mapping → 400
        response = await client.post(
            "/api/legal/config/tst-trt",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "trt_id": trt_id},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["message"]
