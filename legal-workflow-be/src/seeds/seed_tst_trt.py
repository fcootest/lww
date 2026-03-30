"""Seed TST_TRT mappings and TRT roles."""

from src.modules.trt.model import TRT, TST_TRT
from src.modules.trt.repository import trt_repository, tst_trt_repository


TRT_SEED = [
    TRT(trt_id="TRT-001", trt_code="SUBMITTOR", trt_name="Submittor",
        description="Person who submits task input"),
    TRT(trt_id="TRT-002", trt_code="LEGAL_APPROVER", trt_name="Legal Approver",
        description="Person who reviews and approves legal tasks"),
]

# TST_TRT mappings: which roles are needed for which task types
TST_TRT_SEED = [
    # LF211.1 (Chuan bi ban so sanh UI/UX) needs SUBMITTOR
    TST_TRT(tst_id="TST-003", trt_id="TRT-001", is_required=True),
    # LF212.1-5 (Ra soat steps) need LEGAL_APPROVER
    TST_TRT(tst_id="TST-005", trt_id="TRT-002", is_required=True),
    TST_TRT(tst_id="TST-006", trt_id="TRT-002", is_required=True),
    TST_TRT(tst_id="TST-007", trt_id="TRT-002", is_required=True),
    TST_TRT(tst_id="TST-008", trt_id="TRT-002", is_required=True),
    TST_TRT(tst_id="TST-009", trt_id="TRT-002", is_required=True),
]


def seed_all():
    """Seed TRT roles and TST_TRT mappings."""
    for trt in TRT_SEED:
        if trt_repository.get_by_id(trt.trt_id) is None:
            trt_repository.create(trt)
    for mapping in TST_TRT_SEED:
        if not tst_trt_repository.exists(mapping.tst_id, mapping.trt_id):
            tst_trt_repository.create(mapping)
