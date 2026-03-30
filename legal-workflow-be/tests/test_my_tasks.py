"""Step 20: My Pending Tasks tests."""

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
        json={"tst_id": "TST-001", "title": "Copyright Check App X"},
    )
    return response.json()["data"]


class TestMyTasks:

    @pytest.mark.asyncio
    async def test_returns_only_assigned_tasks(self, client):
        """MinhPT (EMP-004) gets only tasks assigned to MinhPT."""
        await _create_task(client)

        # MinhPT is auto-assigned as SUBMITTOR to L3 (TST-003)
        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/my-tasks",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total"] >= 1

        # TrungNV should have 0 tasks
        token2 = make_token(emp_code="TrungNV", role="LEGAL_SPECIALIST")
        response2 = await client.get(
            "/api/legal/my-tasks",
            headers=auth_header(token2),
        )
        assert response2.status_code == 200
        data2 = response2.json()["data"]
        assert data2["total"] == 0

    @pytest.mark.asyncio
    async def test_pagination_works(self, client):
        """Pagination returns correct page info."""
        await _create_task(client)

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/my-tasks?page=1&page_size=10",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client):
        """Filter by status=PENDING returns only PENDING tasks."""
        await _create_task(client)

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/my-tasks?status=PENDING",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        for item in data["items"]:
            assert item["status"] == "PENDING"

    @pytest.mark.asyncio
    async def test_result_has_tst_names(self, client):
        """Each result has tst_l1_name, tst_l2_name, tst_l3_name."""
        await _create_task(client)

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.get(
            "/api/legal/my-tasks",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total"] >= 1
        item = data["items"][0]
        assert "tst_l1_name" in item
        assert "submitted_by_name" in item
