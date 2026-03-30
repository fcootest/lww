"""Tests for SEC PT and CDT filters -- Steps 6 & 7."""

from src.modules.sec.models import SecPermission, SecLevel
from src.modules.sec.filters import pt_filter, cdt_filter, sec_filter

# Sample tasks with filters
TASKS = [
    {"tsi_id": "T1", "title": "Task ED HQ1", "filters": [{"filter_type": "PT", "filter_code": "ED"}, {"filter_type": "CDT", "filter_code": "SHQ1"}]},
    {"tsi_id": "T2", "title": "Task GA AST", "filters": [{"filter_type": "PT", "filter_code": "GA"}, {"filter_type": "CDT", "filter_code": "CAH"}]},
    {"tsi_id": "T3", "title": "Task EN HQ2", "filters": [{"filter_type": "PT", "filter_code": "EN"}, {"filter_type": "CDT", "filter_code": "SHQ2"}]},
    {"tsi_id": "T4", "title": "Task no filter", "filters": []},
    {"tsi_id": "T5", "title": "Task VP VIS", "filters": [{"filter_type": "PT", "filter_code": "VP"}, {"filter_type": "CDT", "filter_code": "CVL"}]},
]

SEC1_HQ1 = SecPermission(
    emp_code="F.00011", emp_name="TrangPH", google_email="trangph@apero.vn",
    empsec=SecLevel.SEC1, pt_allowed="MyPT", cdt_allowed="MyCDT", krf_level=3, cdt_1="HQ1",
)
SEC2_HQ1 = SecPermission(
    emp_code="F.00022", emp_name="OaiNV", google_email="oainv@apero.vn",
    empsec=SecLevel.SEC2, pt_allowed="AllPT", cdt_allowed="MyCDTParent", krf_level=3, cdt_1="HQ1",
)
SEC4 = SecPermission(
    emp_code="F.00041", emp_name="HoangDNH", google_email="hoangdnh@apero.vn",
    empsec=SecLevel.SEC4, pt_allowed="AllPT", cdt_allowed="AllCDT", krf_level=7, cdt_1="AST",
)


class TestPtFilter:

    def test_pt_filter_sec1_sees_only_allowed_pts(self):
        result = pt_filter(TASKS, SEC1_HQ1, allowed_pts=["ED", "GA"])
        ids = [t["tsi_id"] for t in result]
        assert "T1" in ids  # ED
        assert "T2" in ids  # GA
        assert "T3" not in ids  # EN not allowed
        assert "T4" in ids  # no PT filter = visible
        assert "T5" not in ids  # VP not allowed

    def test_pt_filter_sec4_sees_all(self):
        result = pt_filter(TASKS, SEC4)
        assert len(result) == 5

    def test_pt_filter_task_without_pt(self):
        result = pt_filter(TASKS, SEC1_HQ1, allowed_pts=["ED"])
        ids = [t["tsi_id"] for t in result]
        assert "T4" in ids  # no PT = always visible

    def test_pt_filter_empty_allowed(self):
        result = pt_filter(TASKS, SEC1_HQ1, allowed_pts=[])
        ids = [t["tsi_id"] for t in result]
        assert ids == ["T4"]  # only no-filter task

    def test_pt_filter_allpt_source(self):
        result = pt_filter(TASKS, SEC2_HQ1)
        assert len(result) == 5  # AllPT sees all


class TestCdtFilter:

    def test_cdt_filter_sec1_own_cdt_only(self):
        result = cdt_filter(TASKS, SEC1_HQ1)
        ids = [t["tsi_id"] for t in result]
        assert "T1" in ids  # SHQ1 = HQ1
        assert "T2" not in ids  # CAH != SHQ1
        assert "T3" not in ids  # SHQ2 != SHQ1
        assert "T4" in ids  # no CDT = visible

    def test_cdt_filter_sec2_with_parent(self):
        result = cdt_filter(TASKS, SEC2_HQ1)
        ids = [t["tsi_id"] for t in result]
        assert "T1" in ids  # SHQ1 = own CDT
        assert "T4" in ids  # no CDT = visible
        # GAG is parent of SHQ1, other CDTs are siblings under GAG
        # MyCDTParent = [SHQ1, GAG], so only SHQ1 tasks + no-filter

    def test_cdt_filter_sec4_all(self):
        result = cdt_filter(TASKS, SEC4)
        assert len(result) == 5

    def test_combined_pt_and_cdt_filter(self):
        result = sec_filter(TASKS, SEC1_HQ1, allowed_pts=["ED", "GA"])
        ids = [t["tsi_id"] for t in result]
        assert "T1" in ids  # ED + SHQ1 = pass both
        assert "T2" not in ids  # GA ok but CAH != SHQ1
        assert "T4" in ids  # no filter = pass both

    def test_task_without_cdt(self):
        result = cdt_filter(TASKS, SEC1_HQ1)
        ids = [t["tsi_id"] for t in result]
        assert "T4" in ids
