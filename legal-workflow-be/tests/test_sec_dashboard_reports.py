"""Tests for SEC-filtered dashboard and reports -- Step 8."""

from src.modules.sec.models import SecPermission, SecLevel
from src.modules.sec.filters import sec_filter

TASKS = [
    {"tsi_id": "T1", "status": "IN_PROGRESS", "filters": [{"filter_type": "PT", "filter_code": "ED"}, {"filter_type": "CDT", "filter_code": "SHQ1"}]},
    {"tsi_id": "T2", "status": "COMPLETED", "filters": [{"filter_type": "PT", "filter_code": "GA"}, {"filter_type": "CDT", "filter_code": "CAH"}]},
    {"tsi_id": "T3", "status": "IN_PROGRESS", "filters": [{"filter_type": "PT", "filter_code": "EN"}, {"filter_type": "CDT", "filter_code": "SHQ2"}]},
    {"tsi_id": "T4", "status": "PENDING", "filters": []},
]

SEC1 = SecPermission(
    emp_code="F.00011", emp_name="TrangPH", google_email="trangph@apero.vn",
    empsec=SecLevel.SEC1, pt_allowed="MyPT", cdt_allowed="MyCDT", krf_level=3, cdt_1="HQ1",
)
SEC4 = SecPermission(
    emp_code="F.00041", emp_name="HoangDNH", google_email="hoangdnh@apero.vn",
    empsec=SecLevel.SEC4, pt_allowed="AllPT", cdt_allowed="AllCDT", krf_level=7, cdt_1="AST",
)


class TestDashboardFiltered:

    def test_dashboard_sec1_filtered(self):
        filtered = sec_filter(TASKS, SEC1, allowed_pts=["ED"])
        assert len(filtered) == 2  # T1 (ED+SHQ1) + T4 (no filter)

    def test_dashboard_sec4_all(self):
        filtered = sec_filter(TASKS, SEC4)
        assert len(filtered) == 4

    def test_sla_report_filtered(self):
        filtered = sec_filter(TASKS, SEC1, allowed_pts=["ED", "GA"])
        in_progress = [t for t in filtered if t["status"] == "IN_PROGRESS"]
        assert len(in_progress) == 1  # only T1

    def test_workload_report_filtered(self):
        filtered = sec_filter(TASKS, SEC1, allowed_pts=[])
        assert len(filtered) == 1  # only T4 (no filter)

    def test_reports_with_no_tasks_in_scope(self):
        empty_sec1 = SecPermission(
            emp_code="F.99", emp_name="Nobody", google_email="nobody@apero.vn",
            empsec=SecLevel.SEC1, pt_allowed="MyPT", cdt_allowed="MyCDT", krf_level=3, cdt_1="ZZZ",
        )
        filtered = sec_filter(TASKS, empty_sec1, allowed_pts=[])
        # only tasks with no filter pass
        assert all(len(t["filters"]) == 0 for t in filtered)
