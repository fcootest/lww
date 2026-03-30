"""Tests for SEC permission data models -- Step 0."""

import pytest
from src.modules.sec.models import SecLevel, SecPermission


class TestSecLevelEnum:
    """Test SecLevel enum values."""

    def test_sec_level_enum(self):
        """SEC1-SEC4 are valid; invalid value raises error."""
        assert SecLevel.SEC1 == "SEC1"
        assert SecLevel.SEC2 == "SEC2"
        assert SecLevel.SEC3 == "SEC3"
        assert SecLevel.SEC4 == "SEC4"
        with pytest.raises(ValueError):
            SecLevel("SEC5")


class TestSecPermissionModel:
    """Test SecPermission Pydantic model."""

    def test_sec_permission_model_valid(self):
        """Construct with all fields -- no error."""
        perm = SecPermission(
            emp_code="F.00011",
            emp_name="TrangPH",
            google_email="trangph@apero.vn",
            empgrade="LX3",
            empsec=SecLevel.SEC1,
            pt_allowed="MyPT",
            cdt_allowed="MyCDT",
            krf_level=3,
            cdt_1="HQ1",
            cdt="SHQ1_Headquarters1 I TTE_Tech",
            role_legal="User",
        )
        assert perm.emp_code == "F.00011"
        assert perm.empsec == SecLevel.SEC1

    def test_sec_permission_model_defaults(self):
        """Minimal construction uses defaults for optional fields."""
        perm = SecPermission(
            emp_code="F.00099",
            emp_name="TestUser",
            google_email="test@apero.vn",
        )
        assert perm.empsec == SecLevel.SEC1
        assert perm.pt_allowed == "MyPT"
        assert perm.cdt_allowed == "MyCDT"
        assert perm.krf_level == 3

    def test_sec_permission_serialization(self):
        """model_dump() returns all expected keys."""
        perm = SecPermission(
            emp_code="F.00011",
            emp_name="TrangPH",
            google_email="trangph@apero.vn",
            empsec=SecLevel.SEC4,
            pt_allowed="AllPT",
            cdt_allowed="AllCDT",
            krf_level=7,
        )
        data = perm.model_dump()
        expected_keys = {
            "emp_code", "emp_name", "google_email", "empgrade",
            "empsec", "pt_allowed", "cdt_allowed", "krf_level",
            "cdt_1", "cdt", "role_legal",
        }
        assert expected_keys == set(data.keys())

    def test_sec_permission_from_bq_row(self):
        """Construct from a dict mimicking BigQuery v_auth_lookup row."""
        bq_row = {
            "emp_code": "F.00041",
            "emp_name": "HoangDNH",
            "google_email": "hoangdnh@apero.vn",
            "empgrade": "SM1",
            "empsec": "SEC4",
            "pt_allowed": "AllPT",
            "cdt_allowed": "AllCDT",
            "krf_level": 7,
            "cdt_1": "AST",
            "cdt": "CAH_Astronex I TAD_App Development",
            "role_legal": "Approver",
        }
        perm = SecPermission(**bq_row)
        assert perm.empsec == SecLevel.SEC4
        assert perm.krf_level == 7
        assert perm.role_legal == "Approver"
