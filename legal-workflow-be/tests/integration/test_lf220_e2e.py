"""LF220 Trademark E2E -- simplified flow create -> approve all -> complete."""

import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from tests.helpers import make_token, auth_header


def _reset_all_repos():
    from src.config.database import reset_db
    reset_db()

    """Clear and re-seed ALL repository singletons."""
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
    from src.seeds.seed_lf220_config import seed_all as s7
    s1(); s2(); s3(); s4(); s5(); s6(); s7()


def _ensure_assigned(tsi_id, emp_id, trt_id):
    from src.modules.tri.repository import tri_repository
    from src.modules.tri.model import TRI
    from src.modules.tsi.repository import tsi_repository
    from uuid import uuid4
    assigns = tri_repository.get_by_tsi(tsi_id)
    if not any(a.emp_id == emp_id for a in assigns):
        tri = TRI(tri_id=f"TRI-{uuid4().hex[:8]}", trt_id=trt_id, tsi_id=tsi_id, emp_id=emp_id)
        tri_repository.create(tri)
        tsi_repository.update(tsi_id, {"assigned_to": emp_id})


def _set_in_progress(tsi_id):
    from src.modules.tsi.repository import tsi_repository
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi and tsi.status.value == "PENDING":
        tsi_repository.update(tsi_id, {"status": "IN_PROGRESS"})


@pytest.fixture(autouse=True)
def reset_repos():
    _reset_all_repos()
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_lf220_full_e2e(client):
    """Full LF220 Trademark E2E: create -> approve all steps -> COMPLETED."""
    from src.modules.tsi.repository import tsi_repository

    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    # Create trademark task
    resp = await client.post(
        "/api/legal/task/",
        headers=auth_header(minh_token),
        json={
            "tst_id": "TST-010",
            "title": "TrademarkCheck - App Icon",
            "filters": [
                {"filter_type": "PT", "filter_code": "APB648"},
                {"filter_type": "LE", "filter_code": "APERO-SG"},
                {"filter_type": "CTY", "filter_code": "VN"},
                {"filter_type": "TUT", "filter_code": "NORMAL"},
            ],
        },
    )
    assert resp.status_code == 201
    l1_id = resp.json()["data"]["tsi_id"]

    # Approve all pending L3 steps iteratively
    processed = set()
    for iteration in range(30):
        all_tsis = tsi_repository.get_all()
        pending_l3s = [
            t for t in all_tsis
            if t.current_tst_level == 3
            and t.status.value in ("PENDING", "IN_PROGRESS")
            and t.tsi_id not in processed
        ]
        if not pending_l3s:
            for t in all_tsis:
                if t.current_tst_level == 2 and t.status.value == "IN_PROGRESS":
                    children = [c for c in all_tsis
                                if c.my_parent_task == t.tsi_id
                                and c.status.value in ("PENDING", "IN_PROGRESS")
                                and c.tsi_id not in processed]
                    pending_l3s.extend(children)
            if not pending_l3s:
                break

        step = pending_l3s[0]
        # Auto-assign if needed (MinhPT for submittor steps, TiepTA for approver)
        from src.modules.trt.repository import tst_trt_repository
        mappings = tst_trt_repository.get_by_tst(step.tst_id)
        if mappings and mappings[0].trt_id == "TRT-001":
            _ensure_assigned(step.tsi_id, "EMP-004", "TRT-001")
            _ensure_assigned(step.tsi_id, "EMP-001", "TRT-002")
            _set_in_progress(step.tsi_id)
            token = tiep_token  # Admin approves
        else:
            _ensure_assigned(step.tsi_id, "EMP-001", "TRT-002")
            _set_in_progress(step.tsi_id)
            token = tiep_token

        resp = await client.post(
            f"/api/legal/task/{step.tsi_id}/approve",
            headers=auth_header(token),
        )
        assert resp.status_code == 200, f"Approve {step.tst_id} failed: {resp.text}"
        processed.add(step.tsi_id)

    # Verify final state
    l1_final = tsi_repository.get_by_id(l1_id)
    assert l1_final.status.value == "COMPLETED", f"L1 not COMPLETED: {l1_final.status.value}"
