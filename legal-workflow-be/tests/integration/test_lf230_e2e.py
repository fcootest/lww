"""LF230 Policy E2E -- create -> approve all steps through 4 phases -> COMPLETED."""

import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from tests.helpers import make_token, auth_header
from tests.integration.e2e_helpers import reset_all_repos, run_workflow_to_completion


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
async def test_lf230_full_e2e(client):
    """Full LF230 Policy E2E: create -> approve all steps -> COMPLETED."""
    from src.modules.tsi.repository import tsi_repository

    minh_token = make_token("MinhPT", "PRODUCT_MANAGER", "Pham Thanh Minh")
    tiep_token = make_token("TiepTA", "LEGAL_MANAGER", "Tran Anh Tiep")

    l1_id = await run_workflow_to_completion(
        client, "TST-021", "PolicyReview - Privacy Policy",
        minh_token, tiep_token, auth_header,
    )

    l1_final = tsi_repository.get_by_id(l1_id)
    assert l1_final.status.value == "COMPLETED", f"L1 not COMPLETED: {l1_final.status.value}"
