"""Step 9: EMP Entity + List API tests."""

import pytest
from tests.helpers import make_token, auth_header


@pytest.fixture(autouse=True)
def seed_data():
    from src.config.database import reset_db
    reset_db()

    """Seed EMP repository before each test."""
    from src.modules.emp.repository import emp_repository
    from src.seeds.seed_emp import EMP_SEED

    emp_repository.clear()
    emp_repository.seed(EMP_SEED)
    yield
    emp_repository.clear()


class TestEMPListAPI:
    """Test GET /api/legal/emp."""

    @pytest.mark.asyncio
    async def test_list_returns_6_employees(self, client):
        """GET returns all 6 seeded employees."""
        token = make_token()
        response = await client.get(
            "/api/legal/emp/",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 6

    @pytest.mark.asyncio
    async def test_filter_department_cdt_legal_returns_3(self, client):
        """GET ?department=CDT-LEGAL returns 3 employees."""
        token = make_token()
        response = await client.get(
            "/api/legal/emp/?department=CDT-LEGAL",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3

    @pytest.mark.asyncio
    async def test_detail_tiep_ta(self, client):
        """GET /emp/TiepTA returns detail."""
        token = make_token()
        response = await client.get(
            "/api/legal/emp/TiepTA",
            headers=auth_header(token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["emp_code"] == "TiepTA"
        assert data["data"]["emp_name"] == "Tran Anh Tiep"
        assert data["data"]["department"] == "CDT-LEGAL"

    @pytest.mark.asyncio
    async def test_detail_nonexistent_returns_404(self, client):
        """GET /emp/NONEXISTENT returns 404."""
        token = make_token()
        response = await client.get(
            "/api/legal/emp/NONEXISTENT",
            headers=auth_header(token),
        )
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
