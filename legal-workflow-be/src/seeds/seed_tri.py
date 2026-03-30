"""Seed TRI base pool — default role assignments."""

from src.modules.tri.model import TRI
from src.modules.tri.repository import tri_repository


TRI_BASE_POOL = [
    # TiepTA as LEGAL_APPROVER (base pool — tsi_id=None)
    TRI(tri_id="TRI-BASE-001", trt_id="TRT-002", tsi_id=None,
        emp_id="EMP-001"),
    # MinhPT as SUBMITTOR (base pool — tsi_id=None)
    TRI(tri_id="TRI-BASE-002", trt_id="TRT-001", tsi_id=None,
        emp_id="EMP-004"),
]


def seed_all():
    """Seed TRI base pool."""
    tri_repository.seed(TRI_BASE_POOL)
