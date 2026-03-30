"""Step 8: Filter Config (TST_Filter + TST_TDT) API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Clean repositories before each test."""
    from src.modules.tst.repository import tst_repository
    from src.modules.tdt.repository import tdt_repository
    from src.modules.filters.repository import tst_filter_repository, tst_tdt_repository
    from src.seeds.seed_tst import ALL_SEED

    tst_repository.clear()
    tst_repository.seed(ALL_SEED)
    tdt_repository.clear()
    tst_filter_repository.clear()
    tst_tdt_repository.clear()
    yield
    tst_repository.clear()
    tdt_repository.clear()
    tst_filter_repository.clear()
    tst_tdt_repository.clear()


class TestTSTFilterAPI:
    """Test POST /api/legal/config/tst-filter."""

    @pytest.mark.asyncio
    async def test_create_tst_filter(self, client):
        """POST /tst-filter creates mapping."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tst-filter",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "filter_type": "TLT",
                "filter_code": "FILTER_001",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tst_id"] == "TST-001"
        assert data["data"]["filter_type"] == "TLT"

    @pytest.mark.asyncio
    async def test_create_with_invalid_filter_type_returns_422(self, client):
        """POST with invalid filter_type returns 422."""
        token = make_token(role="ADMIN")
        response = await client.post(
            "/api/legal/config/tst-filter",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "filter_type": "INVALID_TYPE",
                "filter_code": "FILTER_001",
            },
        )
        assert response.status_code == 422


class TestTSTTDTAPI:
    """Test POST /api/legal/config/tst-tdt."""

    @pytest.mark.asyncio
    async def test_create_tst_tdt_mapping(self, client):
        """POST /tst-tdt creates mapping."""
        token = make_token(role="ADMIN")
        # Create a TDT first
        tdt_resp = await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={"tdt_code": "DOC001", "tdt_name": "Screenshot Doc"},
        )
        tdt_id = tdt_resp.json()["data"]["tdt_id"]

        response = await client.post(
            "/api/legal/config/tst-tdt",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "tdt_id": tdt_id,
                "is_required": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["tst_id"] == "TST-001"
        assert data["data"]["tdt_id"] == tdt_id
        assert data["data"]["is_required"] is True


class TestTSTFullAPI:
    """Test GET /api/legal/config/tst/{id}/full."""

    @pytest.mark.asyncio
    async def test_get_tst_full_includes_filters_and_doc_types(self, client):
        """GET /tst/{id}/full includes filters[] and doc_types[]."""
        token = make_token(role="ADMIN")

        # Create filter
        await client.post(
            "/api/legal/config/tst-filter",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "filter_type": "TMT", "filter_code": "M001"},
        )

        # Create TDT
        tdt_resp = await client.post(
            "/api/legal/config/tdt/",
            headers=auth_header(token),
            json={"tdt_code": "DOC010", "tdt_name": "Policy Doc"},
        )
        tdt_id = tdt_resp.json()["data"]["tdt_id"]

        # Map TDT to TST
        await client.post(
            "/api/legal/config/tst-tdt",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "tdt_id": tdt_id},
        )

        # Get full TST
        response = await client.get(
            "/api/legal/config/tst/TST-001/full",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "filters" in data
        assert "doc_types" in data
        assert len(data["filters"]) == 1
        assert data["filters"][0]["filter_type"] == "TMT"
        assert len(data["doc_types"]) == 1
        assert data["doc_types"][0]["tdt_id"] == tdt_id
