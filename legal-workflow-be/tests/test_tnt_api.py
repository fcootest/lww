"""Step 5: TNT Config CRUD API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Ensure repositories are seeded before each test."""
    from src.modules.tst.repository import tst_repository
    from src.modules.tnt.repository import tnt_repository
    from src.seeds.seed_tst import ALL_SEED
    from src.seeds.seed_tnt import LF210_TNT_SEED

    tst_repository.clear()
    tst_repository.seed(ALL_SEED)
    tnt_repository.clear()
    tnt_repository.seed(LF210_TNT_SEED)
    yield
    tst_repository.clear()
    tnt_repository.clear()


class TestTNTListAPI:
    """Test GET /api/legal/config/tnt."""

    @pytest.mark.asyncio
    async def test_get_with_from_tst_id_returns_filtered(self, client):
        """GET with from_tst_id returns filtered list."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tnt/",
            params={"from_tst_id": "TST-002"},
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        items = data["data"]
        assert len(items) >= 2  # TNT-001 and TNT-008 both from TST-002
        assert all(item["from_tst_id"] == "TST-002" for item in items)

    @pytest.mark.asyncio
    async def test_get_all_returns_all(self, client):
        """GET without filter returns all."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tnt/",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 8


class TestTNTCreateAPI:
    """Test POST /api/legal/config/tnt."""

    @pytest.mark.asyncio
    async def test_create_tnt(self, client):
        """POST creates TNT."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tnt/",
            headers=auth_header(token),
            json={
                "from_tst_id": "TST-001",
                "to_tst_id": "TST-002",
                "priority": 1,
                "condition_description": "Start copyright check",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["from_tst_id"] == "TST-001"
        assert data["data"]["tnt_id"].startswith("TNT-")

    @pytest.mark.asyncio
    async def test_create_with_nonexistent_from_tst_returns_400(self, client):
        """POST with nonexistent from_tst_id returns 400."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tnt/",
            headers=auth_header(token),
            json={
                "from_tst_id": "NONEXISTENT",
                "to_tst_id": "TST-002",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_condition_expression_stored_as_json_string(self, client):
        """condition_expression stored as JSON string."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tnt/",
            headers=auth_header(token),
            json={
                "from_tst_id": "TST-001",
                "to_tst_id": "TST-002",
                "condition_expression": '{"auto_approve": true}',
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["condition_expression"] == '{"auto_approve": true}'


class TestTNTDeleteAPI:
    """Test DELETE /api/legal/config/tnt."""

    @pytest.mark.asyncio
    async def test_delete_works(self, client):
        """DELETE works."""
        token = make_token(role="ADMIN")
        response = await client.delete(
            "/api/legal/config/tnt/TNT-001",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Deleted"
