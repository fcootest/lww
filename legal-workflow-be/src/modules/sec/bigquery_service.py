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
        # JOIN with fps_data.emp_list to get the correct id_number as emp_code
        # v_auth_lookup.emp_code may be '#N/A' for some users; id_number is authoritative
        query = """
            SELECT
                v.google_email,
                COALESCE(
                    NULLIF(e.id_number, '#N/A'),
                    NULLIF(v.emp_code, '#N/A'),
                    v.emp_code
                ) AS emp_code,
                v.emp_name,
                v.empgrade,
                v.empsec,
                v.pt_allowed,
                v.cdt_allowed,
                v.krf_level,
                v.cdt_1,
                v.cdt,
                v.role_legal
            FROM `fp-a-project.sec_data.v_auth_lookup` v
            LEFT JOIN `fp-a-project.fps_data.emp_list` e
                ON v.emp_name = e.id_name
            WHERE v.google_email = @email
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
