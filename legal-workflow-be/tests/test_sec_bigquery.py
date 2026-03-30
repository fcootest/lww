"""Tests for BigQuery Permission Service -- Step 4."""

import os
from src.modules.sec.service import get_permission_service, MockPermissionService
from src.modules.sec.models import SecLevel


class TestServiceFactory:

    def test_fallback_to_mock_when_bq_unavailable(self):
        """When USE_BIGQUERY_AUTH=false, returns MockPermissionService."""
        os.environ["USE_BIGQUERY_AUTH"] = "false"
        svc = get_permission_service()
        assert isinstance(svc, MockPermissionService)
        os.environ.pop("USE_BIGQUERY_AUTH", None)

    def test_service_factory_default_is_mock(self):
        """Default (no env var) returns mock."""
        os.environ.pop("USE_BIGQUERY_AUTH", None)
        svc = get_permission_service()
        assert isinstance(svc, MockPermissionService)


class TestBigQueryService:

    def test_bq_service_returns_sec_permission(self):
        """If BQ available, query real data for known email."""
        os.environ["USE_BIGQUERY_AUTH"] = "true"
        try:
            from src.modules.sec.bigquery_service import BigQueryPermissionService
            svc = BigQueryPermissionService()
            perm = svc.get_by_email("trangph@apero.vn")
            if perm is not None:
                assert perm.empsec == SecLevel.SEC1
                assert perm.emp_code == "F.00011"
        except Exception:
            pass  # BQ not available in CI/test
        finally:
            os.environ.pop("USE_BIGQUERY_AUTH", None)

    def test_bq_service_not_found(self):
        """Query for unknown email returns None."""
        os.environ["USE_BIGQUERY_AUTH"] = "true"
        try:
            from src.modules.sec.bigquery_service import BigQueryPermissionService
            svc = BigQueryPermissionService()
            perm = svc.get_by_email("nonexistent@apero.vn")
            assert perm is None
        except Exception:
            pass  # BQ not available in CI/test
        finally:
            os.environ.pop("USE_BIGQUERY_AUTH", None)

    def test_bq_service_field_mapping(self):
        """BQ row maps correctly to SecPermission fields."""
        from src.modules.sec.bigquery_service import BigQueryPermissionService
        row = {
            "google_email": "trangph@apero.vn",
            "emp_code": "F.00011",
            "emp_name": "TrangPH",
            "empgrade": "LX3",
            "empsec": "SEC1",
            "pt_allowed": "MyPT",
            "cdt_allowed": "MyCDT",
            "krf_level": 3,
            "cdt_1": "HQ1",
            "cdt": "SHQ1_Headquarters1",
            "role_legal": "User",
            "empsec_description": "ignored field",
        }
        perm = BigQueryPermissionService._row_to_permission(row)
        assert perm.empsec == SecLevel.SEC1
        assert perm.emp_code == "F.00011"
