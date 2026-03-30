"""Step 15: Document Upload TDI tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Seed and clean repositories before each test."""
    from src.modules.tst.repository import tst_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tsi_filter.repository import tsi_filter_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.trt.repository import trt_repository, tst_trt_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tdi.repository import tdi_repository
    from src.seeds.seed_tst import ALL_SEED
    from src.seeds.seed_emp import EMP_SEED
    from src.seeds.seed_tst_trt import TRT_SEED, TST_TRT_SEED
    from src.seeds.seed_tri import TRI_BASE_POOL

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()
    tdi_repository.clear()

    tst_repository.seed(ALL_SEED)
    emp_repository.seed(EMP_SEED)
    for trt in TRT_SEED:
        trt_repository.create(trt)
    for m in TST_TRT_SEED:
        tst_trt_repository.create(m)
    tri_repository.seed(TRI_BASE_POOL)

    yield

    tst_repository.clear()
    tsi_repository.clear()
    tsi_filter_repository.clear()
    tsev_repository.clear()
    emp_repository.clear()
    trt_repository.clear()
    tst_trt_repository.clear()
    tri_repository.clear()
    tdi_repository.clear()


async def _create_task(client, token):
    """Helper to create a task and return the L1 TSI."""
    response = await client.post(
        "/api/legal/task/",
        headers=auth_header(token),
        json={
            "tst_id": "TST-001",
            "title": "Test Task for Docs",
        },
    )
    return response.json()["data"]


class TestTDIDocumentUpload:
    """Test POST /api/legal/task/{tsi_id}/document."""

    @pytest.mark.asyncio
    async def test_upload_document_returns_201(self, client):
        """POST creates TDI -> 201."""
        token = make_token()
        task = await _create_task(client, token)

        response = await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-001",
                "file_name": "comparison.pdf",
                "file_url": "https://storage.example.com/docs/comparison.pdf",
                "notes": "Initial upload",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["file_name"] == "comparison.pdf"
        assert data["data"]["version"] == 1
        assert data["data"]["tdi_id"].startswith("TDI-")

    @pytest.mark.asyncio
    async def test_tsev_upload_event_created(self, client):
        """TSEV UPLOAD event is created."""
        from src.modules.tsev.repository import tsev_repository

        token = make_token()
        task = await _create_task(client, token)

        # Clear events from task creation
        tsev_repository.clear()

        await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-001",
                "file_name": "doc.pdf",
                "file_url": "https://storage.example.com/doc.pdf",
            },
        )

        events = tsev_repository.get_by_tsi(task["tsi_id"])
        upload_events = [e for e in events if e.event_type.value == "UPLOAD"]
        assert len(upload_events) == 1

    @pytest.mark.asyncio
    async def test_second_upload_same_tdt_version_2(self, client):
        """Second upload same TDT -> version=2."""
        token = make_token()
        task = await _create_task(client, token)

        # First upload
        await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-001",
                "file_name": "v1.pdf",
                "file_url": "https://storage.example.com/v1.pdf",
            },
        )

        # Second upload same TDT
        response = await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-001",
                "file_name": "v2.pdf",
                "file_url": "https://storage.example.com/v2.pdf",
            },
        )
        assert response.status_code == 201
        assert response.json()["data"]["version"] == 2

    @pytest.mark.asyncio
    async def test_get_documents_list(self, client):
        """GET returns doc list."""
        token = make_token()
        task = await _create_task(client, token)

        # Upload two docs
        await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-001",
                "file_name": "doc1.pdf",
                "file_url": "https://storage.example.com/doc1.pdf",
            },
        )
        await client.post(
            f"/api/legal/task/{task['tsi_id']}/document",
            headers=auth_header(token),
            json={
                "tdt_id": "TDT-002",
                "file_name": "doc2.pdf",
                "file_url": "https://storage.example.com/doc2.pdf",
            },
        )

        response = await client.get(
            f"/api/legal/task/{task['tsi_id']}/documents",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
