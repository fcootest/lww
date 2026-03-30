"""Step 33: SLA + Workload Reports tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Seed all repositories."""
    from src.modules.tst.repository import tst_repository
    from src.modules.tnt.repository import tnt_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.tdi.repository import tdi_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.trt.repository import trt_repository, tst_trt_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.tsi_filter.repository import tsi_filter_repository
    from src.modules.tdt.repository import tdt_repository
    from src.modules.filters.repository import tst_filter_repository as cfg1
    from src.modules.filters.repository import tst_tdt_repository

    for repo in [tst_repository, tnt_repository, tsi_repository, tsev_repository,
                 tdi_repository, tri_repository, trt_repository, tst_trt_repository,
                 emp_repository, tsi_filter_repository, tdt_repository, cfg1, tst_tdt_repository]:
        repo.clear()

    from src.seeds.seed_tst import seed_all as s1
    from src.seeds.seed_tnt import seed_all as s2
    from src.seeds.seed_emp import seed_all as s3
    from src.seeds.seed_tst_trt import seed_all as s4
    from src.seeds.seed_tri import seed_all as s5
    from src.seeds.seed_lf210_config import seed_all as s6
    s1(); s2(); s3(); s4(); s5(); s6()
    yield


class TestSLAReport:
    @pytest.mark.asyncio
    async def test_sla_report_returns_data_structure(self, client):
        """SLA report returns correct data structure."""
        token = make_token(role="LEGAL_MANAGER")
        resp = await client.get(
            "/api/legal/reports/sla",
            headers=auth_header(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Even with no tasks, structure should be valid
        for item in data["data"]:
            assert "tst_id" in item
            assert "tst_name" in item
            assert "on_time" in item
            assert "late" in item
            assert "sla_compliance_rate" in item


class TestWorkloadReport:
    @pytest.mark.asyncio
    async def test_workload_report_returns_data_structure(self, client):
        """Workload report returns correct data structure."""
        token = make_token(role="LEGAL_MANAGER")
        resp = await client.get(
            "/api/legal/reports/workload",
            headers=auth_header(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        for item in data["data"]:
            assert "emp_id" in item
            assert "emp_code" in item
            assert "task_count" in item
            assert "completed_count" in item
            assert "pending_count" in item
