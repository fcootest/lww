"""Step 11 + 13: Auto-navigate TST Tree + Auto-assignment tests."""

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


class TestAutoNavigate:

    @pytest.mark.asyncio
    async def test_create_l1_auto_creates_l2_and_l3(self, client):
        from src.modules.tsi.repository import tsi_repository
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        assert response.status_code == 201
        all_tsis = tsi_repository.get_all()
        assert len(all_tsis) == 3
        l2 = [t for t in all_tsis if t.tst_id == "TST-002"]
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"]
        assert len(l2) == 1
        assert len(l3) == 1

    @pytest.mark.asyncio
    async def test_l2_parent_is_l1(self, client):
        from src.modules.tsi.repository import tsi_repository
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        tsi_l1_id = response.json()["data"]["tsi_id"]
        all_tsis = tsi_repository.get_all()
        l2 = [t for t in all_tsis if t.tst_id == "TST-002"][0]
        assert l2.my_parent_task == tsi_l1_id

    @pytest.mark.asyncio
    async def test_l3_parent_is_l2(self, client):
        from src.modules.tsi.repository import tsi_repository
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        all_tsis = tsi_repository.get_all()
        l2 = [t for t in all_tsis if t.tst_id == "TST-002"][0]
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"][0]
        assert l3.my_parent_task == l2.tsi_id

    @pytest.mark.asyncio
    async def test_filters_copied_to_l2_and_l3(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tsi_filter.repository import tsi_filter_repository
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={
                "tst_id": "TST-001",
                "title": "Copyright Check App X",
                "filters": [
                    {"filter_type": "CDT", "filter_code": "CDT-PRODUCT"},
                    {"filter_type": "PT", "filter_code": "PT-MOBILE"},
                ],
            },
        )
        tsi_l1_id = response.json()["data"]["tsi_id"]
        all_tsis = tsi_repository.get_all()
        l2 = [t for t in all_tsis if t.tst_id == "TST-002"][0]
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"][0]
        assert len(tsi_filter_repository.get_by_tsi(tsi_l1_id)) == 2
        assert len(tsi_filter_repository.get_by_tsi(l2.tsi_id)) == 2
        assert len(tsi_filter_repository.get_by_tsi(l3.tsi_id)) == 2

    @pytest.mark.asyncio
    async def test_l2_in_progress_l3_pending(self, client):
        from src.modules.tsi.repository import tsi_repository
        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        all_tsis = tsi_repository.get_all()
        l2 = [t for t in all_tsis if t.tst_id == "TST-002"][0]
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"][0]
        assert l2.status.value == "IN_PROGRESS"
        assert l3.status.value == "PENDING"

    @pytest.mark.asyncio
    async def test_l3_auto_assigned_when_matching_tri(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.tri.repository import tri_repository
        token = make_token()
        await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"][0]
        assert l3.assigned_to == "EMP-004"
        tris = tri_repository.get_by_tsi(l3.tsi_id)
        assert len(tris) >= 1

    @pytest.mark.asyncio
    async def test_no_matching_role_stays_pending(self, client):
        from src.modules.tsi.repository import tsi_repository
        from src.modules.trt.repository import tst_trt_repository
        from src.config.database import get_db
        get_db().execute("DELETE FROM tst_trt WHERE tst_id=?", ("TST-003",))
        get_db().commit()
        token = make_token()
        response = await client.post(
            "/api/legal/task/",
            headers=auth_header(token),
            json={"tst_id": "TST-001", "title": "Copyright Check App X"},
        )
        assert response.status_code == 201
        all_tsis = tsi_repository.get_all()
        l3 = [t for t in all_tsis if t.tst_id == "TST-003"][0]
        assert l3.assigned_to is None
