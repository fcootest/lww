"""Step 18: Phase Completion tests."""

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


def _ensure_assigned(tri_repository, tsi_id, emp_id, trt_id):
    from uuid import uuid4
    from src.modules.tri.model import TRI
    if not tri_repository.exists(tsi_id, emp_id, trt_id):
        tri_repository.create(TRI(
            tri_id=f"TRI-{uuid4().hex[:8]}",
            trt_id=trt_id,
            tsi_id=tsi_id,
            emp_id=emp_id,
        ))


async def _create_and_get_l3(client, tsi_repository, tri_repository):
    """Create task and return the first L3 TSI."""
    token = make_token()
    await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={"tst_id": "TST-001", "title": "Copyright Check App X"},
    )
    all_tsis = tsi_repository.get_all()
    l3 = [t for t in all_tsis if t.current_tst_level == 3][0]
    return l3


async def _approve_l3(client, tsi_repository, tri_repository, l3, emp_code, emp_id, trt_id):
    """Set L3 to IN_PROGRESS, ensure assigned, and approve."""
    tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})
    _ensure_assigned(tri_repository, l3.tsi_id, emp_id, trt_id)
    token = make_token(emp_code=emp_code, role="LEGAL_MANAGER")
    response = await client.post(
        f"/api/legal/task/{l3.tsi_id}/approve",
        headers=auth_header(token),
    )
    return response


class TestPhaseCompletion:

    @pytest.mark.asyncio
    async def test_approve_last_l3_in_phase_creates_next_l2(self, client):
        """Approve last L3 in LF211 phase -> L2 COMPLETED -> creates L2 for LF212 + first L3."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        from src.modules.tnt.repository import tnt_repository

        # Clear TNT so no step-level transitions exist (force phase completion)
        tnt_repository.clear()

        l3 = await _create_and_get_l3(client, tsi_repository, tri_repository)
        # This L3 is TST-003 (LF211.1) - only L3 under LF211

        await _approve_l3(client, tsi_repository, tri_repository, l3, "MinhPT", "EMP-004", "TRT-001")

        all_tsis = tsi_repository.get_all()

        # L2 for LF211 should be COMPLETED
        l2_lf211 = [t for t in all_tsis if t.tst_id == "TST-002"][0]
        assert l2_lf211.status.value == "COMPLETED"

        # New L2 for LF212 (TST-004) should be created
        l2_lf212 = [t for t in all_tsis if t.tst_id == "TST-004"]
        assert len(l2_lf212) == 1
        assert l2_lf212[0].status.value == "IN_PROGRESS"

        # First L3 under LF212 (TST-005) should be created
        l3_lf212_1 = [t for t in all_tsis if t.tst_id == "TST-005"]
        assert len(l3_lf212_1) == 1

    @pytest.mark.asyncio
    async def test_all_phases_complete_marks_l1_completed(self, client):
        """Approve all L3s in all phases -> L1 COMPLETED (workflow done)."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        from src.modules.tnt.repository import tnt_repository

        # Clear TNT to simplify -- each L3 completion triggers phase completion
        tnt_repository.clear()

        # Create task
        l3 = await _create_and_get_l3(client, tsi_repository, tri_repository)

        # Phase 1: Approve LF211.1 (TST-003)
        await _approve_l3(client, tsi_repository, tri_repository, l3, "MinhPT", "EMP-004", "TRT-001")

        # Phase 2: Now LF212 is created. Approve LF212.1 (TST-005)
        all_tsis = tsi_repository.get_all()
        l3_lf212_1 = [t for t in all_tsis if t.tst_id == "TST-005"][0]
        await _approve_l3(client, tsi_repository, tri_repository, l3_lf212_1, "TiepTA", "EMP-001", "TRT-002")

        # Check L1 status
        all_tsis = tsi_repository.get_all()
        l1 = [t for t in all_tsis if t.current_tst_level == 1][0]
        assert l1.status.value == "COMPLETED"

    @pytest.mark.asyncio
    async def test_workflow_completed_event_logged(self, client):
        """TSEV UPDATE with Workflow completed logged on L1."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        from src.modules.tnt.repository import tnt_repository
        from src.modules.tsev.repository import tsev_repository

        tnt_repository.clear()

        l3 = await _create_and_get_l3(client, tsi_repository, tri_repository)
        await _approve_l3(client, tsi_repository, tri_repository, l3, "MinhPT", "EMP-004", "TRT-001")

        all_tsis = tsi_repository.get_all()
        l3_lf212_1 = [t for t in all_tsis if t.tst_id == "TST-005"][0]
        await _approve_l3(client, tsi_repository, tri_repository, l3_lf212_1, "TiepTA", "EMP-001", "TRT-002")

        all_tsis = tsi_repository.get_all()
        l1 = [t for t in all_tsis if t.current_tst_level == 1][0]
        events = tsev_repository.get_by_tsi(l1.tsi_id)
        update_events = [e for e in events if e.event_type.value == "UPDATE"]
        assert len(update_events) >= 1
        assert any("Workflow completed" in (e.event_data or "") for e in update_events)

    @pytest.mark.asyncio
    async def test_l1_status_completed_at_end(self, client):
        """L1 status = COMPLETED at the end of workflow."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        from src.modules.tnt.repository import tnt_repository

        tnt_repository.clear()

        l3 = await _create_and_get_l3(client, tsi_repository, tri_repository)
        await _approve_l3(client, tsi_repository, tri_repository, l3, "MinhPT", "EMP-004", "TRT-001")

        all_tsis = tsi_repository.get_all()
        l3_lf212_1 = [t for t in all_tsis if t.tst_id == "TST-005"][0]
        await _approve_l3(client, tsi_repository, tri_repository, l3_lf212_1, "TiepTA", "EMP-001", "TRT-002")

        all_tsis = tsi_repository.get_all()
        l1 = [t for t in all_tsis if t.current_tst_level == 1][0]
        assert l1.status.value == "COMPLETED"
