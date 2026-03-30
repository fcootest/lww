"""Step 19: Reject Action tests."""

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


class TestReject:

    @pytest.mark.asyncio
    async def test_reject_tsi_sets_rejected(self, client):
        """Reject TSI -> REJECTED + TSEV logged."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository

        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Test Task"},
        )

        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.current_tst_level == 3][0]
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})

        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        token_emp = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/reject",
            headers=auth_header(token_emp),
            json={"reason": "Missing documents"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "REJECTED"

    @pytest.mark.asyncio
    async def test_reject_with_reason_in_event(self, client):
        """Reject with reason stored in event_data."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        from src.modules.tsev.repository import tsev_repository
        import json

        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Test Task"},
        )

        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.current_tst_level == 3][0]
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})

        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        token_emp = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        await client.post(
            f"/api/legal/task/{l3.tsi_id}/reject",
            headers=auth_header(token_emp),
            json={"reason": "Missing documents"},
        )

        events = tsev_repository.get_by_tsi(l3.tsi_id)
        reject_events = [e for e in events if e.event_type.value == "REJECT"]
        assert len(reject_events) == 1
        event_data = json.loads(reject_events[0].event_data)
        assert event_data["reason"] == "Missing documents"

    @pytest.mark.asyncio
    async def test_reject_not_assigned_403(self, client):
        """Non-assigned employee cannot reject."""
        from src.modules.tsi.repository import tsi_repository

        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Test Task"},
        )

        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.current_tst_level == 3][0]
        tsi_repository.update(l3.tsi_id, {"status": "IN_PROGRESS"})

        token_other = make_token(emp_code="TrungNV", role="LEGAL_SPECIALIST")
        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/reject",
            headers=auth_header(token_other),
            json={"reason": "Test"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_reject_pending_auto_transitions(self, client):
        """Reject PENDING auto-transitions then rejects."""
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository

        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Test Task"},
        )

        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.current_tst_level == 3][0]
        # L3 is PENDING, not IN_PROGRESS
        _ensure_assigned(tri_repository, l3.tsi_id, "EMP-004", "TRT-001")

        token_emp = make_token(emp_code="MinhPT", role="LEGAL_MANAGER")
        response = await client.post(
            f"/api/legal/task/{l3.tsi_id}/reject",
            headers=auth_header(token_emp),
            json={"reason": "Test"},
        )
        assert response.status_code == 200
