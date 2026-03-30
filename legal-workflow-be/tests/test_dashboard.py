"""Step 22: Dashboard Summary tests."""

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


async def _create_task(client, tst_id="TST-001", title="Copyright Check App X"):
    token = make_token()
    response = await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={"tst_id": tst_id, "title": title},
    )
    return response.json()["data"]


class TestDashboard:

    @pytest.mark.asyncio
    async def test_returns_summary_counts(self, client):
        """Returns summary with pending, in_progress, completed, overdue."""
        await _create_task(client)
        token = make_token(role="ADMIN")
        response = await client.get(
            "/api/legal/dashboard",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "summary" in data
        summary = data["summary"]
        assert "pending" in summary
        assert "in_progress" in summary
        assert "completed" in summary
        assert "overdue" in summary

    @pytest.mark.asyncio
    async def test_returns_by_type_breakdown(self, client):
        """Returns by_type with copyright, trademark, policy, contract counts."""
        await _create_task(client)
        token = make_token(role="ADMIN")
        response = await client.get(
            "/api/legal/dashboard",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "by_type" in data
        by_type = data["by_type"]
        assert "copyright" in by_type
        assert "trademark" in by_type
        assert "policy" in by_type
        assert "contract" in by_type
        assert by_type["copyright"] >= 1

    @pytest.mark.asyncio
    async def test_admin_sees_all_tasks(self, client):
        """Admin sees all tasks in dashboard."""
        await _create_task(client)

        # Admin token
        token_admin = make_token(emp_code="TiepTA", role="ADMIN")
        response = await client.get(
            "/api/legal/dashboard",
            headers=auth_header(token_admin),
        )
        assert response.status_code == 200
        data = response.json()["data"]
        summary = data["summary"]
        total = summary["pending"] + summary["in_progress"] + summary["completed"]
        assert total >= 1
