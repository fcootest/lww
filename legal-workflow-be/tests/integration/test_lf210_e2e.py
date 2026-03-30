"""
LF210 CopyrightReview E2E -- matches AP Appendix A.2.
App: Caller ID Spam Call and Message (APB648, APERO-SG, IN)
Submitter: MinhPT (Product Manager)
Reviewer: TiepTA (Legal Manager)
Expected: 9+ TSI, 10+ TSEV, 2+ TDI
"""

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
    from src.modules.filters.repository import tst_filter_repository as tst_filter_cfg
    from src.modules.filters.repository import tst_tdt_repository

    for repo in [tst_repository, tnt_repository, tsi_repository, tsev_repository,
                 tdi_repository, tri_repository, trt_repository, tst_trt_repository,
                 emp_repository, tsi_filter_repository, tdt_repository,
                 tst_filter_cfg, tst_tdt_repository]:
        repo.clear()

    from src.seeds.seed_tst import seed_all as s1
    from src.seeds.seed_tnt import seed_all as s2
    from src.seeds.seed_emp import seed_all as s3
    from src.seeds.seed_tst_trt import seed_all as s4
    from src.seeds.seed_tri import seed_all as s5
    from src.seeds.seed_lf210_config import seed_all as s6
    s1(); s2(); s3(); s4(); s5(); s6()


def _ensure_assigned(tsi_id, emp_id, trt_id):
    """Ensure employee is assigned to task."""
    from src.modules.tri.repository import tri_repository
    from src.modules.tri.model import TRI
    from src.modules.tsi.repository import tsi_repository
    from uuid import uuid4
    assigns = tri_repository.get_by_tsi(tsi_id)
    if not any(a.emp_id == emp_id for a in assigns):
        tri = TRI(
            tri_id=f"TRI-{uuid4().hex[:8]}",
            trt_id=trt_id,
            tsi_id=tsi_id,
            emp_id=emp_id,
        )
        tri_repository.create(tri)
        tsi_repository.update(tsi_id, {"assigned_to": emp_id})


def _set_in_progress(tsi_id):
    """Set TSI status to IN_PROGRESS if it is PENDING."""
    from src.modules.tsi.repository import tsi_repository
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi and tsi.status.value == "PENDING":
        tsi_repository.update(tsi_id, {"status": "IN_PROGRESS"})


@pytest.fixture(autouse=True)
def reset_repos():
    """Reset all repositories before each test."""
    _reset_all_repos()
    yield


@pytest.fixture
async def client():
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_lf210_full_e2e(client):
    """Full LF210 CopyrightReview E2E workflow test."""
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.tdi.repository import tdi_repository

    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    # Stage 1: MinhPT creates task
    resp = await client.post(
        "/api/legal/task/",
        headers=auth_header(minh_token),
        json={
            "tst_id": "TST-001",
            "title": "CopyrightReview - Caller ID",
            "filters": [
                {"filter_type": "PT", "filter_code": "APB648"},
                {"filter_type": "LE", "filter_code": "APERO-SG"},
                {"filter_type": "CTY", "filter_code": "IN"},
                {"filter_type": "TUT", "filter_code": "NORMAL"},
            ],
        },
    )
    assert resp.status_code == 201, f"Create task failed: {resp.text}"
    l1_id = resp.json()["data"]["tsi_id"]

    # Stage 2: Verify auto-navigate created L2(LF211) + L3(LF211.1)
    all_tsis = tsi_repository.get_all()
    l2_tsis = [t for t in all_tsis if t.my_parent_task == l1_id]
    assert len(l2_tsis) == 1
    l2_lf211 = l2_tsis[0]
    assert l2_lf211.tst_id == "TST-002"

    l3_tsis = [t for t in all_tsis if t.my_parent_task == l2_lf211.tsi_id]
    assert len(l3_tsis) == 1
    l3_id = l3_tsis[0].tsi_id

    # Stage 3: Verify auto-assign MinhPT (SUBMITTOR)
    from src.modules.tri.repository import tri_repository
    assignments = tri_repository.get_by_tsi(l3_id)
    assert any(a.emp_id == "EMP-004" for a in assignments)

    # Stage 4: MinhPT uploads doc
    resp = await client.post(
        f"/api/legal/task/{l3_id}/document",
        headers=auth_header(minh_token),
        json={
            "tdt_id": "TDT-001",
            "file_name": "ui_comparison_v1.pdf",
            "file_url": "https://storage.example.com/ui_comparison_v1.pdf",
        },
    )
    assert resp.status_code == 201

    # Stage 5: Admin approves LF211.1
    _ensure_assigned(l3_id, "EMP-001", "TRT-002")
    _set_in_progress(l3_id)
    resp = await client.post(
        f"/api/legal/task/{l3_id}/approve",
        headers=auth_header(tiep_token),
    )
    assert resp.status_code == 200

    # Follow the workflow through all remaining steps
    processed = {l3_id}

    for iteration in range(20):
        all_tsis = tsi_repository.get_all()
        pending_l3s = [
            t for t in all_tsis
            if t.current_tst_level == 3
            and t.status.value in ("PENDING", "IN_PROGRESS")
            and t.tsi_id not in processed
        ]
        if not pending_l3s:
            for t in all_tsis:
                if (t.current_tst_level == 2
                        and t.status.value == "IN_PROGRESS"):
                    children = [c for c in all_tsis
                                if c.my_parent_task == t.tsi_id
                                and c.status.value in ("PENDING", "IN_PROGRESS")
                                and c.tsi_id not in processed]
                    pending_l3s.extend(children)
            if not pending_l3s:
                break

        step = pending_l3s[0]
        _ensure_assigned(step.tsi_id, "EMP-001", "TRT-002")
        _set_in_progress(step.tsi_id)

        if step.tst_id == "TST-009":
            resp = await client.post(
                f"/api/legal/task/{step.tsi_id}/document",
                headers=auth_header(tiep_token),
                json={
                    "tdt_id": "TDT-004",
                    "file_name": "copyright_report_v1.pdf",
                    "file_url": "https://storage.example.com/copyright_report.pdf",
                },
            )
            assert resp.status_code == 201

        resp = await client.post(
            f"/api/legal/task/{step.tsi_id}/approve",
            headers=auth_header(tiep_token),
        )
        assert resp.status_code == 200, f"Approve {step.tst_id} failed: {resp.text}"
        processed.add(step.tsi_id)

    # Final verification
    all_tsis = tsi_repository.get_all()
    l1_final = tsi_repository.get_by_id(l1_id)
    assert l1_final.status.value == "COMPLETED", f"L1 not COMPLETED: {l1_final.status.value}"

    total_tsev = sum(len(tsev_repository.get_by_tsi(t.tsi_id)) for t in all_tsis)
    total_tdi = sum(len(tdi_repository.get_by_tsi(t.tsi_id)) for t in all_tsis)

    assert len(all_tsis) >= 9, f"Expected >= 9 TSI, got {len(all_tsis)}"
    assert total_tsev >= 10, f"Expected >= 10 TSEV, got {total_tsev}"
    assert total_tdi >= 2, f"Expected >= 2 TDI, got {total_tdi}"
