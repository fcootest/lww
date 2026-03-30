"""E2E Integration Tests for SEC Permission Flow -- Step 13."""

from fastapi.testclient import TestClient
from src.app import app
from src.auth.jwt_utils import decode_jwt
from src.modules.sec.models import SecLevel
from src.modules.sec.filters import sec_filter

client = TestClient(app)

TASKS_WITH_FILTERS = [
    {"tsi_id": "T1", "title": "Copyright HQ1", "status": "IN_PROGRESS",
     "filters": [{"filter_type": "PT", "filter_code": "ED"}, {"filter_type": "CDT", "filter_code": "SHQ1"}]},
    {"tsi_id": "T2", "title": "Trademark AST", "status": "PENDING",
     "filters": [{"filter_type": "PT", "filter_code": "GA"}, {"filter_type": "CDT", "filter_code": "CAH"}]},
    {"tsi_id": "T3", "title": "Policy HQ2", "status": "COMPLETED",
     "filters": [{"filter_type": "PT", "filter_code": "EN"}, {"filter_type": "CDT", "filter_code": "SHQ2"}]},
    {"tsi_id": "T4", "title": "Global task", "status": "IN_PROGRESS",
     "filters": []},
]


class TestE2ESecFlow:

    def _login(self, email: str) -> dict:
        resp = client.post("/api/auth/login", json={"email": email})
        assert resp.status_code == 200
        data = resp.json()["data"]
        return data

    def test_e2e_sec1_full_flow(self):
        """SEC1 login -> filtered tasks -> only own PT+CDT visible."""
        data = self._login("trangph@apero.vn")
        token = data["token"]
        user = data["user"]

        # Verify JWT contains SEC fields
        payload = decode_jwt(token)
        assert payload["empsec"] == "SEC1"
        assert payload["pt_allowed"] == "MyPT"
        assert payload["cdt_allowed"] == "MyCDT"
        assert payload["krf_level"] == 3

        # Simulate filtering tasks
        from src.modules.sec.models import SecPermission
        sec = SecPermission(**user)
        filtered = sec_filter(TASKS_WITH_FILTERS, sec, allowed_pts=["ED"])

        # SEC1 HQ1 with PT=ED: should see T1 (ED+SHQ1) + T4 (no filter)
        ids = [t["tsi_id"] for t in filtered]
        assert "T1" in ids
        assert "T4" in ids
        assert "T2" not in ids  # wrong CDT
        assert "T3" not in ids  # wrong PT and CDT

    def test_e2e_sec4_full_flow(self):
        """SEC4 login -> all tasks visible."""
        data = self._login("hoangdnh@apero.vn")
        token = data["token"]
        user = data["user"]

        payload = decode_jwt(token)
        assert payload["empsec"] == "SEC4"
        assert payload["pt_allowed"] == "AllPT"
        assert payload["cdt_allowed"] == "AllCDT"

        from src.modules.sec.models import SecPermission
        sec = SecPermission(**user)
        filtered = sec_filter(TASKS_WITH_FILTERS, sec)
        assert len(filtered) == 4  # all tasks visible

    def test_e2e_cross_sec_isolation(self):
        """SEC1 in HQ1 cannot see AST tasks; SEC4 can see all."""
        sec1_data = self._login("trangph@apero.vn")
        sec4_data = self._login("hoangdnh@apero.vn")

        from src.modules.sec.models import SecPermission
        sec1 = SecPermission(**sec1_data["user"])
        sec4 = SecPermission(**sec4_data["user"])

        sec1_filtered = sec_filter(TASKS_WITH_FILTERS, sec1, allowed_pts=["ED", "GA"])
        sec4_filtered = sec_filter(TASKS_WITH_FILTERS, sec4)

        # SEC1 HQ1 cannot see T2 (AST) or T3 (HQ2)
        sec1_ids = [t["tsi_id"] for t in sec1_filtered]
        assert "T2" not in sec1_ids
        assert "T3" not in sec1_ids

        # SEC4 sees everything
        assert len(sec4_filtered) == 4

    def test_e2e_dashboard_filtering(self):
        """Each SEC level gets correctly scoped counts."""
        logins = {
            "SEC1": "trangph@apero.vn",
            "SEC2": "oainv@apero.vn",
            "SEC3": "giangpnt@apero.vn",
            "SEC4": "hoangdnh@apero.vn",
        }

        from src.modules.sec.models import SecPermission
        counts = {}
        for level, email in logins.items():
            data = self._login(email)
            sec = SecPermission(**data["user"])
            filtered = sec_filter(TASKS_WITH_FILTERS, sec,
                                  allowed_pts=["ED"] if level == "SEC1" else None)
            counts[level] = len(filtered)

        # SEC1 sees least, SEC4 sees most
        assert counts["SEC1"] <= counts["SEC4"]
        assert counts["SEC4"] == 4

    def test_e2e_sec2_sees_parent_cdt(self):
        """SEC2 (MyCDTParent) sees tasks in own CDT + parent."""
        data = self._login("oainv@apero.vn")

        from src.modules.sec.models import SecPermission
        sec = SecPermission(**data["user"])
        # SEC2 has AllPT, so PT filter passes all
        # CDT: MyCDTParent for HQ1 = [SHQ1, GAG]
        filtered = sec_filter(TASKS_WITH_FILTERS, sec)

        ids = [t["tsi_id"] for t in filtered]
        assert "T1" in ids  # SHQ1 = own CDT
        assert "T4" in ids  # no filter
        # T2 (CAH) and T3 (SHQ2) are NOT in [SHQ1, GAG] as CDT codes
        # (GAG is not a task CDT code in our test data)

    def test_e2e_all_sec_levels_can_login(self):
        """All 4 mock users can successfully login and get SEC permissions."""
        emails = ["trangph@apero.vn", "oainv@apero.vn", "giangpnt@apero.vn", "hoangdnh@apero.vn"]
        expected_levels = [SecLevel.SEC1, SecLevel.SEC2, SecLevel.SEC3, SecLevel.SEC4]

        for email, expected in zip(emails, expected_levels):
            data = self._login(email)
            assert data["user"]["empsec"] == expected.value
            assert data["token"] is not None
            payload = decode_jwt(data["token"])
            assert payload["empsec"] == expected.value
