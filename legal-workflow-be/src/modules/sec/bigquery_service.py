"""BigQuery Permission Service -- queries sec_data.v_auth_lookup."""

from typing import Optional
from src.modules.sec.models import SecPermission


class BigQueryPermissionService:
    """Queries BigQuery for SEC permissions."""

    BQ_FIELDS = [
        "google_email", "emp_code", "emp_name", "empgrade",
        "empsec", "pt_allowed", "cdt_allowed", "krf_level",
        "cdt_1", "cdt", "role_legal",
    ]

    def __init__(self):
        try:
            from google.cloud import bigquery
            self._client = bigquery.Client(project="fp-a-project")
        except Exception as e:
            raise RuntimeError(f"BigQuery client init failed: {e}")

    def get_by_email(self, email: str) -> Optional[SecPermission]:
        query = """
            SELECT google_email, emp_code, emp_name, empgrade,
                   empsec, pt_allowed, cdt_allowed, krf_level,
                   cdt_1, cdt, role_legal
            FROM `fp-a-project.sec_data.v_auth_lookup`
            WHERE google_email = @email
            LIMIT 1
        """
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email.lower())]
        )
        rows = list(self._client.query(query, job_config=job_config).result())
        if not rows:
            return None
        return self._row_to_permission(dict(rows[0]))

    @staticmethod
    def _row_to_permission(row: dict) -> SecPermission:
        """Convert a BQ row dict to SecPermission."""
        filtered = {k: v for k, v in row.items() if k in BigQueryPermissionService.BQ_FIELDS}
        return SecPermission(**filtered)
