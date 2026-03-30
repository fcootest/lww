"""
Step 35: Final Integration Test -- runs ALL 4 workflow E2E flows,
verifies dashboard, my-tasks, and repo counts.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from tests.helpers import make_token, auth_header
from tests.integration.e2e_helpers import (
    reset_all_repos, run_workflow_to_completion,
)


@pytest.fixture(autouse=True)
def reset_repos():
    reset_all_repos()
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_all_4_workflows_complete(client):
    """Run all 4 workflow types to completion."""
    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")
    from src.modules.tsi.repository import tsi_repository

    # LF210 Copyright
    l1_210 = await run_workflow_to_completion(
        client, "TST-001", "Copyright - Final Test",
        minh_token, tiep_token, auth_header,
    )
    assert tsi_repository.get_by_id(l1_210).status.value == "COMPLETED"

    # LF220 Trademark
    l1_220 = await run_workflow_to_completion(
        client, "TST-010", "Trademark - Final Test",
        minh_token, tiep_token, auth_header,
    )
    assert tsi_repository.get_by_id(l1_220).status.value == "COMPLETED"

    # LF230 Policy
    l1_230 = await run_workflow_to_completion(
        client, "TST-021", "Policy - Final Test",
        minh_token, tiep_token, auth_header,
    )
    assert tsi_repository.get_by_id(l1_230).status.value == "COMPLETED"

    # LF240 Contract
    l1_240 = await run_workflow_to_completion(
        client, "TST-034", "Contract - Final Test",
        minh_token, tiep_token, auth_header,
    )
    assert tsi_repository.get_by_id(l1_240).status.value == "COMPLETED"


@pytest.mark.asyncio
async def test_dashboard_shows_correct_counts(client):
    """After all 4 workflows, dashboard shows correct by_type counts."""
    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    await run_workflow_to_completion(client, "TST-001", "Copyright Test", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-010", "Trademark Test", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-021", "Policy Test", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-034", "Contract Test", minh_token, tiep_token, auth_header)

    admin_token = make_token("TiepTA", "ADMIN", "Tran Anh Tiep")
    resp = await client.get("/api/legal/dashboard", headers=auth_header(admin_token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    by_type = data["by_type"]
    assert by_type["copyright"] >= 1
    assert by_type["trademark"] >= 1
    assert by_type["policy"] >= 1
    assert by_type["contract"] >= 1


@pytest.mark.asyncio
async def test_my_tasks_returns_for_both_users(client):
    """My-tasks returns tasks for both MinhPT and TiepTA."""
    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    await run_workflow_to_completion(client, "TST-001", "Copyright MyTasks", minh_token, tiep_token, auth_header)

    # MinhPT should have tasks
    resp = await client.get("/api/legal/my-tasks", headers=auth_header(minh_token))
    assert resp.status_code == 200
    minh_data = resp.json()["data"]
    assert minh_data["total"] >= 1

    # TiepTA should have tasks
    resp = await client.get("/api/legal/my-tasks", headers=auth_header(tiep_token))
    assert resp.status_code == 200
    tiep_data = resp.json()["data"]
    assert tiep_data["total"] >= 1


@pytest.mark.asyncio
async def test_repos_have_correct_total_counts(client):
    """All repos have correct total record counts after 4 workflows."""
    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    await run_workflow_to_completion(client, "TST-001", "Copyright Count", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-010", "Trademark Count", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-021", "Policy Count", minh_token, tiep_token, auth_header)
    await run_workflow_to_completion(client, "TST-034", "Contract Count", minh_token, tiep_token, auth_header)

    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tst.repository import tst_repository

    all_tsis = tsi_repository.get_all()
    all_tsts = tst_repository.get_all()

    # We should have 52 TST records (9 + 11 + 13 + 19)
    assert len(all_tsts) == 52, f"Expected 52 TST, got {len(all_tsts)}"

    # At least 4 L1 TSIs (one per workflow)
    l1_count = sum(1 for t in all_tsis if t.current_tst_level == 1)
    assert l1_count == 4, f"Expected 4 L1 TSI, got {l1_count}"

    # All L1 should be COMPLETED
    l1_completed = sum(1 for t in all_tsis if t.current_tst_level == 1 and t.status.value == "COMPLETED")
    assert l1_completed == 4, f"Expected 4 completed L1 TSI, got {l1_completed}"

    # TRI should have assignments
    all_tris = tri_repository.get_all()
    assert len(all_tris) >= 8, f"Expected >= 8 TRI, got {len(all_tris)}"
