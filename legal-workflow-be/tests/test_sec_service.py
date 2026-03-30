"""Tests for SEC Mock Permission Service -- Step 1."""

from src.modules.sec.service import MockPermissionService
from src.modules.sec.models import SecLevel


class TestMockPermissionService:

    def setup_method(self):
        self.svc = MockPermissionService()

    def test_get_by_email_sec1(self):
        perm = self.svc.get_by_email("trangph@apero.vn")
        assert perm is not None
        assert perm.empsec == SecLevel.SEC1
        assert perm.pt_allowed == "MyPT"
        assert perm.cdt_allowed == "MyCDT"
        assert perm.krf_level == 3

    def test_get_by_email_sec4(self):
        perm = self.svc.get_by_email("hoangdnh@apero.vn")
        assert perm is not None
        assert perm.empsec == SecLevel.SEC4
        assert perm.pt_allowed == "AllPT"
        assert perm.cdt_allowed == "AllCDT"
        assert perm.krf_level == 7

    def test_get_by_email_not_found(self):
        perm = self.svc.get_by_email("unknown@apero.vn")
        assert perm is None

    def test_get_by_email_case_insensitive(self):
        perm = self.svc.get_by_email("TrangPH@apero.vn")
        assert perm is not None
        assert perm.emp_name == "TrangPH"

    def test_service_returns_all_fields(self):
        perm = self.svc.get_by_email("trangph@apero.vn")
        assert perm.emp_code is not None
        assert perm.emp_name is not None
        assert perm.google_email is not None
        assert perm.empsec is not None
        assert perm.pt_allowed is not None
        assert perm.cdt_allowed is not None
        assert perm.krf_level is not None
        assert perm.cdt_1 is not None
        assert perm.role_legal is not None
