"""Step 21: Task Detail View tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    from src.modules.tst.repository import tst_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsi_filter.repository import tsi_filter_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.trt.repository import trt_repository, tst_trt_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tnt.repository import tnt_repository
    from src.seeds.seed_tst import ALL_SEED
    from src.seeds.seed_emp import EMP_SEED
    from src.seeds.seed_tst_trt import TRT_SEED, TST_TRT_SEED
    from src.seeds.seed_tri import TRI_BASE_POOL
    from src.seeds.seed_tnt import LF210_TNT_SEED

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()
    tnt_repository.clear()

    tst_repository.seed(ALL_SEED)
    emp_repository.seed(EMP_SEED)
    for trt in TRT_SEED:
        trt_repository.create(trt)
    for m in TST_TRT_SEED:
        tst_trt_repository.create(m)
    tri_repository.seed(TRI_BASE_POOL)
    tnt_repository.seed(LF210_TNT_SEED)

    yield

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()
    tnt_repository.clear()


async def _create_task(client):
    token = make_token()
    response = await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={
            "tst_id": "TST-001",
            "title": "Copyright Check App X",
            "filters": [
                {"filter_type": "CDT", "filter_code": "CDT-PRODUCT"},
            ],
        },
    )
    return response.json()["data"]


class TestTaskDetail:

    @pytest.mark.asyncio
    async def test_returns_full_structure(self, client):
        """Returns full structure with progress[], documents[], events[], filters."""
        task = await _create_task(client)
        token = make_token()

        response = await client.get(
            f"/api/legal/task/{task['tsi_id']}",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "tsi" in data
        assert "progress" in data
        assert "documents" in data
        assert "events" in data
        assert "filters" in data

    @pytest.mark.asyncio
    async def test_progress_shows_tst_tree(self, client):
        """Progress shows TST tree with status per node."""
        task = await _create_task(client)
        token = make_token()

        response = await client.get(
            f"/api/legal/task/{task['tsi_id']}",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        progress = data["progress"]
        assert len(progress) >= 1

        # L1 node
        l1_node = progress[0]
        assert l1_node["tst_level"] == 1
        assert "status" in l1_node
        assert "children" in l1_node
        assert len(l1_node["children"]) >= 1

        # L2 node
        l2_node = l1_node["children"][0]
        assert l2_node["tst_level"] == 2
        assert "children" in l2_node

    @pytest.mark.asyncio
    async def test_nonexistent_tsi_returns_404(self, client):
        """Nonexistent TSI returns 404."""
        token = make_token()
        response = await client.get(
            "/api/legal/task/NONEXISTENT",
            headers=auth_header(token),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_events_ordered_by_created_at(self, client):
        """Events are ordered by created_at."""
        task = await _create_task(client)
        token = make_token()

        response = await client.get(
            f"/api/legal/task/{task['tsi_id']}",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        events = data["events"]
        if len(events) >= 2:
            for i in range(len(events) - 1):
                assert events[i]["created_at"] <= events[i + 1]["created_at"]
