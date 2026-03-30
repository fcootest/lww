"""Step 4: TST Config CRUD API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_tst_data():
    """Ensure TST repository is seeded before each test."""
    from src.modules.tst.repository import tst_repository
    from src.seeds.seed_tst import ALL_SEED
    tst_repository.clear()
    tst_repository.seed(ALL_SEED)
    yield
    tst_repository.clear()


class TestTSTListAPI:
    """Test GET /api/legal/config/tst."""

    @pytest.mark.asyncio
    async def test_get_tree_returns_200(self, client):
        """GET / returns tree with valid token."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tst/",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_tree_has_children(self, client):
        """GET / returns tree with nested children."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tst/",
            headers=auth_header(token),
        )
        data = response.json()
        root = data["data"][0]
        assert "children" in root
        assert len(root["children"]) > 0


class TestTSTDetailAPI:
    """Test GET /api/legal/config/tst/{tst_id}."""

    @pytest.mark.asyncio
    async def test_get_detail_returns_tst(self, client):
        """GET /{id} returns detail."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tst/TST-001",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tst_id"] == "TST-001"
        assert data["data"]["tst_code"] == "LF210"

    @pytest.mark.asyncio
    async def test_get_detail_not_found(self, client):
        """GET /{id} for nonexistent returns 404."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/config/tst/NONEXISTENT",
            headers=auth_header(token),
        )
        assert response.status_code == 404


class TestTSTCreateAPI:
    """Test POST /api/legal/config/tst."""

    @pytest.mark.asyncio
    async def test_create_l2_with_parent(self, client):
        """POST creates TST L2 with parent."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tst/",
            headers=auth_header(token),
            json={
                "tst_code": "LF299",
                "tst_name": "New L2 Task",
                "tst_level": 2,
                "my_parent_task": "TST-001",
                "sla_days": 3,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tst_code"] == "LF299"
        assert data["data"]["tst_level"] == 2
        assert data["data"]["tst_id"].startswith("TST-")

    @pytest.mark.asyncio
    async def test_create_without_required_field_returns_422(self, client):
        """POST without required field returns 422."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tst/",
            headers=auth_header(token),
            json={
                "tst_code": "LF999",
                # missing tst_name, tst_level
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_with_nonexistent_parent_returns_400(self, client):
        """POST with nonexistent parent returns 400."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tst/",
            headers=auth_header(token),
            json={
                "tst_code": "LF999",
                "tst_name": "Orphan L2",
                "tst_level": 2,
                "my_parent_task": "NONEXISTENT",
            },
        )
        assert response.status_code == 400


class TestTSTUpdateAPI:
    """Test PUT /api/legal/config/tst/{tst_id}."""

    @pytest.mark.asyncio
    async def test_update_name(self, client):
        """PUT updates name."""
        token = make_token(role="ADMIN")
        response = await client.put(
            "/api/legal/config/tst/TST-001",
            headers=auth_header(token),
            json={"tst_name": "Updated Copyright Check"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["tst_name"] == "Updated Copyright Check"


class TestTSTDeleteAPI:
    """Test DELETE /api/legal/config/tst/{tst_id}."""

    @pytest.mark.asyncio
    async def test_soft_delete(self, client):
        """DELETE soft-deletes TST."""
        token = make_token(role="ADMIN")
        response = await client.delete(
            "/api/legal/config/tst/TST-009",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Deleted"

        # Verify it's gone
        response2 = await client.get(
            "/api/legal/config/tst/TST-009",
            headers=auth_header(token),
        )
        assert response2.status_code == 404


class TestTSTAuthz:
    """Test authorization for TST write operations."""

    @pytest.mark.asyncio
    async def test_non_admin_post_returns_403(self, client):
        """Non-ADMIN token returns 403 for POST."""
        token = make_token(role="LEGAL_MANAGER")
        response = await client.post(
            "/api/legal/config/tst/",
            headers=auth_header(token),
            json={"tst_code": "X", "tst_name": "X", "tst_level": 1},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_non_admin_put_returns_403(self, client):
        """Non-ADMIN token returns 403 for PUT."""
        token = make_token(role="LEGAL_INTERN")
        response = await client.put(
            "/api/legal/config/tst/TST-001",
            headers=auth_header(token),
            json={"tst_name": "Hacked"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_non_admin_delete_returns_403(self, client):
        """Non-ADMIN token returns 403 for DELETE."""
        token = make_token(role="LEGAL_INTERN")
        response = await client.delete(
            "/api/legal/config/tst/TST-001",
            headers=auth_header(token),
        )
        assert response.status_code == 403
