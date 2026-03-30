"""Step 12: TRI Role Assignment tests."""

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

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()

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


async def _create_task(client, token):
    """Helper to create a task and return the L1 TSI."""
    response = await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={
            "tst_id": "TST-001",
            "title": "Test Task for Assignment",
        },
    )
    return response.json()["data"]


class TestTRIAssignment:
    """Test POST /api/legal/tri."""

    @pytest.mark.asyncio
    async def test_assign_emp_to_task_returns_201(self, client):
        """POST assigns TiepTA(LEGAL_APPROVER) to TSI -> 201."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            "/api/legal/tri/",
            headers=auth_header(token),
            json={
                "trt_id": "TRT-002",  # LEGAL_APPROVER
                "tsi_id": task["tsi_id"],
                "emp_id": "EMP-001",  # TiepTA
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["trt_id"] == "TRT-002"
        assert data["data"]["emp_id"] == "EMP-001"

    @pytest.mark.asyncio
    async def test_tsi_assigned_to_updated(self, client):
        """TSI.assigned_to is updated after assignment."""
        from src.modules.tsi.repository import tsi_repository

        token = make_token()
        task = await _create_task(client, token)

        await client.post(
            "/api/legal/tri/",
            headers=auth_header(token),
            json={
                "trt_id": "TRT-002",
                "tsi_id": task["tsi_id"],
                "emp_id": "EMP-001",
            },
        )

        tsi = tsi_repository.get_by_id(task["tsi_id"])
        assert tsi.assigned_to == "EMP-001"

    @pytest.mark.asyncio
    async def test_already_assigned_returns_400(self, client):
        """Already assigned returns 400."""
        token = make_token()
        task = await _create_task(client, token)

        # First assignment
        await client.post(
            "/api/legal/tri/",
            headers=auth_header(token),
            json={
                "trt_id": "TRT-002",
                "tsi_id": task["tsi_id"],
                "emp_id": "EMP-001",
            },
        )

        # Duplicate assignment
        response = await client.post(
            "/api/legal/tri/",
            headers=auth_header(token),
            json={
                "trt_id": "TRT-002",
                "tsi_id": task["tsi_id"],
                "emp_id": "EMP-001",
            },
        )
        assert response.status_code == 400
        assert "already assigned" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_nonexistent_emp_returns_400(self, client):
        """Nonexistent EMP returns 400."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            "/api/legal/tri/",
            headers=auth_header(token),
            json={
                "trt_id": "TRT-002",
                "tsi_id": task["tsi_id"],
                "emp_id": "EMP-999",
            },
        )
        assert response.status_code == 400
        assert "not found" in response.json()["message"]
