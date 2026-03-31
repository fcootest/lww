"""SEC Permission Service -- mock, BigQuery, and factory."""

import os
from typing import Optional
from src.modules.sec.models import SecPermission, SecLevel


# Hardcoded exceptions for non-@apero emails (e.g. external testers)
EXCEPTION_USERS = [
    SecPermission(
        emp_code="F.00000", emp_name="Nguyen Viet Trung", google_email="nguyenvietrung187@gmail.com",
        empgrade="LX1", empsec=SecLevel.SEC1, pt_allowed="MyPT",
        cdt_allowed="MyCDT", krf_level=3, cdt_1="HQ1",
        cdt="SHQ1_Headquarters1 I TTE_Tech", role_legal="User",
    ),
]


class MockPermissionService:
    """Returns hardcoded SEC permissions for testing (4 users, one per level)."""

    MOCK_DATA = [
        SecPermission(
            emp_code="F.00011", emp_name="TrangPH", google_email="trangph@apero.vn",
            empgrade="LX3", empsec=SecLevel.SEC1, pt_allowed="MyPT",
            cdt_allowed="MyCDT", krf_level=3, cdt_1="HQ1",
            cdt="SHQ1_Headquarters1 I TTE_Tech I I TTES_SQA", role_legal="User",
        ),
        SecPermission(
            emp_code="F.00022", emp_name="OaiNV", google_email="oainv@apero.vn",
            empgrade="PX0", empsec=SecLevel.SEC2, pt_allowed="AllPT",
            cdt_allowed="MyCDTParent", krf_level=3, cdt_1="HQ1",
            cdt="SHQ1_Headquarters1 I TDA_Data", role_legal="User",
        ),
        SecPermission(
            emp_code="F.00061", emp_name="GiangPNT", google_email="giangpnt@apero.vn",
            empgrade="TM0", empsec=SecLevel.SEC3, pt_allowed="AllPT",
            cdt_allowed="MyCDT", krf_level=7, cdt_1="AST",
            cdt="CAH_Astronex I TAM_Marketing", role_legal="User",
        ),
        SecPermission(
            emp_code="F.00041", emp_name="HoangDNH", google_email="hoangdnh@apero.vn",
            empgrade="SM1", empsec=SecLevel.SEC4, pt_allowed="AllPT",
            cdt_allowed="AllCDT", krf_level=7, cdt_1="AST",
            cdt="CAH_Astronex I TAD_App Development", role_legal="Approver",
        ),
        SecPermission(
            emp_code="F.00001", emp_name="Trung NV", google_email="trungnv1@apero.vn",
            empgrade="GM", empsec=SecLevel.SEC4, pt_allowed="AllPT",
            cdt_allowed="AllCDT", krf_level=7, cdt_1="HQ1",
            cdt="GAG_Apero Group", role_legal="Approver",
        ),
        SecPermission(
            emp_code="F.00011", emp_name="Tran Anh Tiep", google_email="tiepta@apero.vn",
            empgrade="SM1", empsec=SecLevel.SEC4, pt_allowed="AllPT",
            cdt_allowed="AllCDT", krf_level=7, cdt_1="HQ1",
            cdt="SHQ1_Headquarters1 I TTE_Tech I I TTES_Legal", role_legal="Approver",
        ),
    ] + EXCEPTION_USERS

    def get_by_email(self, email: str) -> Optional[SecPermission]:
        email_lower = email.lower()
        for perm in self.MOCK_DATA:
            if perm.google_email == email_lower:
                return perm
        return None


class CombinedPermissionService:
    """BigQuery first, then fallback to exception users list."""

    def __init__(self, bq_service):
        self._bq = bq_service

    def get_by_email(self, email: str) -> Optional[SecPermission]:
        # Try BigQuery first
        perm = self._bq.get_by_email(email)
        if perm:
            return perm
        # Fallback: check exception users (non-@apero)
        email_lower = email.lower()
        for exc in EXCEPTION_USERS:
            if exc.google_email == email_lower:
                return exc
        return None


def get_permission_service():
    """Factory: returns Combined (BQ + exceptions) if enabled, else Mock."""
    use_bq = os.environ.get("USE_BIGQUERY_AUTH", "false").lower() == "true"
    if use_bq:
        try:
            from src.modules.sec.bigquery_service import BigQueryPermissionService
            bq_svc = BigQueryPermissionService()
            return CombinedPermissionService(bq_svc)
        except Exception:
            pass
    return MockPermissionService()
