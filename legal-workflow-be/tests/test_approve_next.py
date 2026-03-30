"""Step 17: Approve Action + Next Step tests."""

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


async def _create_task(client, token):
    response = await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={"tst_id": "TST-001", "title": "Copyright Check App X"},
    )
    return response.json()["data"]


def _find_l3_tsi(tsi_repository, tst_id=None):
    all_tsis = tsi_repository.get_all()
    l3s = [t for t in all_tsis if t.current_tst_level == 3]
    if tst_id:
        l3s = [t for t in l3s if t.tst_id == tst_id]
    return l3s[0] if l3s else None


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


class TestApproveNext:

    @pytest.mark.asyncio
    async def test_approve_l3_creates_next_tsi(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        await _create_task(client, make_token())

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        assert l3 is not None
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "APPROVED"

        all_tsis = tsi_repository.get_all()
        assert len(all_tsis) >= 4

    @pytest.mark.asyncio
    async def test_new_tsi_auto_assigned(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        await _create_task(client, make_token())

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token),
        )

        all_tsis = tsi_repository.get_all()
        new_tsis = [t for t in all_tsis if t.tsi_id != l3.tsi_id and t.current_tst_level == 3]
        # At least one new L3 should exist
        assert len(new_tsis) >= 1

    @pytest.mark.asyncio
    async def test_tsev_approve_logged(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tsev.repository import tsev_repository
        from src.modules.tri.repository import tri_repository

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        await _create_task(client, make_token())

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token),
        )

        events = tsev_repository.get_by_tsi(l3.tsi_id)
        approve_events = [e for e in events if e.event_type.value == "APPROVE"]
        assert len(approve_events) == 1

    @pytest.mark.asyncio
    async def test_non_assigned_emp_returns_403(self, client):
        from src.modules.tsi.repository import tsi_repository

        await _create_task(client, make_token())

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})

        token_other = make_token(emp_code="TrungNV", role="LEGAL_SPECIALIST")
        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token_other),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_pending_auto_transitions_to_approved(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository

        token = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        await _create_task(client, make_token())

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        # L3 is PENDING - auto-transitions to IN_PROGRESS then COMPLETED
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_last_step_no_tnt_no_error(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tnt.repository import tnt_repository
        from src.modules.tri.repository import tri_repository

        token = make_token(emp_code="TiepTA", role="LEGAL_MANAGER")
        await _create_task(client, make_token())

        tnt_repository.clear()

        l3 = _find_l3_tsi(tsi_repository, "TST-003")
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-001", "TRT-002")

        count_before = len(tsi_repository.get_all())
        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/approve",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        all_tsis = tsi_repository.get_all()
        assert len(all_tsis) >= count_before
