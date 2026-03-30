"""Step 10: Create Task — TSI L1 + TSI_Filter + TSEV tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Seed and clean repositories before each test."""
    from src.modules.tst.repository import tst_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsi_filter.repository import tsi_filter_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.trt.repository import trt_repository, tst_trt_repository
    from src.modules.tri.repository import tri_repository
    from src.seeds.seed_tst import ALL_SEED
    from src.seeds.seed_emp import EMP_SEED
    from src.seeds.seed_tst_trt import TRT_SEED, TST_TRT_SEED
    from src.seeds.seed_tri import TRI_BASE_POOL

    # Clear all
    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()

    # Seed
    tst_repository.seed(ALL_SEED)
    emp_repository.seed(EMP_SEED)
    for trt in TRT_SEED:
        trt_repository.create(trt)
    for m in TST_TRT_SEED:
        tst_trt_repository.create(m)
    tri_repository.seed(TRI_BASE_POOL)

    yield

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()


class TestCreateTaskL1:
    """Test POST /api/legal/task."""

    @pytest.mark.asyncio
    async def test_create_tsi_l1_returns_201(self, client):
        """POST creates TSI L1 with status=IN_PROGRESS."""
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",  # LF210 Copyright Check (L1)
                "title": "Copyright Check for App X",
                "description": "Check copyright compliance",
                "priority": "HIGH",
                "filters": [
                    {"filter_type": "CDT", "filter_code": "CDT-PRODUCT"},
                    {"filter_type": "PT", "filter_code": "PT-MOBILE"},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "IN_PROGRESS"
        assert data["data"]["tst_id"] == "TST-001"
        assert data["data"]["title"] == "Copyright Check for App X"

    @pytest.mark.asyncio
    async def test_tsi_filter_rows_created(self, client):
        """TSI_Filter rows are created with correct count."""
        from src.modules.tsi_filter.repository import tsi_filter_repository

        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "title": "Test Task",
                "filters": [
                    {"filter_type": "CDT", "filter_code": "CDT-PRODUCT"},
                    {"filter_type": "PT", "filter_code": "PT-MOBILE"},
                ],
            },
        )
        assert response.status_code == 201
        tsi_id = response.json()["data"]["tsi_id"]
        filters = tsi_filter_repository.get_by_tsi(tsi_id)
        assert len(filters) == 2

    @pytest.mark.asyncio
    async def test_tsev_create_event_logged(self, client):
        """TSEV CREATE event is logged."""
        from src.modules.tsev.repository import tsev_repository

        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "title": "Test Task",
            },
        )
        assert response.status_code == 201
        tsi_id = response.json()["data"]["tsi_id"]
        events = tsev_repository.get_by_tsi(tsi_id)
        assert len(events) >= 1
        create_events = [e for e in events if e.event_type.value == "CREATE"]
        assert len(create_events) == 1

    @pytest.mark.asyncio
    async def test_tst_level2_returns_400(self, client):
        """POST with tst_id pointing to Level 2 returns 400."""
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-002",  # LF211 (Level 2)
                "title": "Should fail",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert "level" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_auto_generates_tsi_code(self, client):
        """TSI code is auto-generated in TSI-YYYYMMDD-NNN format."""
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "title": "Test Task",
            },
        )
        assert response.status_code == 201
        tsi_code = response.json()["data"]["tsi_code"]
        assert tsi_code.startswith("TSI-")
        # Format: TSI-YYYYMMDD-NNN
        parts = tsi_code.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 3  # NNN

    @pytest.mark.asyncio
    async def test_missing_title_returns_422(self, client):
        """Missing title returns 422."""
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
            },
        )
        assert response.status_code == 422
