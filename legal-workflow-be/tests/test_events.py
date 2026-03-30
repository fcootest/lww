"""Step 14: TSEV Task Event Logging tests."""

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
            "title": "Test Task for Events",
        },
    )
    return response.json()["data"]


class TestTSEVEvents:
    """Test POST /api/legal/task/{tsi_id}/event."""

    @pytest.mark.asyncio
    async def test_create_comment_event_returns_201(self, client):
        """POST event type=COMMENT -> 201."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            f"/api/legal/task/{task['tsi_id']}/event",
            headers=auth_header(token),
            json={
                "event_type": "COMMENT",
                "event_data": '{"text": "Looking good"}',
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["event_type"] == "COMMENT"

    @pytest.mark.asyncio
    async def test_event_data_stored_as_json(self, client):
        """event_data stored as JSON string."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            f"/api/legal/task/{task['tsi_id']}/event",
            headers=auth_header(token),
            json={
                "event_type": "COMMENT",
                "event_data": '{"key": "value", "count": 42}',
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["event_data"] == '{"key": "value", "count": 42}'

    @pytest.mark.asyncio
    async def test_invalid_event_type_returns_422(self, client):
        """Invalid event_type -> 422."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            f"/api/legal/task/{task['tsi_id']}/event",
            headers=auth_header(token),
            json={
                "event_type": "INVALID_TYPE",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_auth_required(self, client):
        """Auth required for event creation."""
        response = await client.post(
            "/api/legal/task/TSI-fake/event",
            json={
                "event_type": "COMMENT",
            },
        )
        assert response.status_code == 401
