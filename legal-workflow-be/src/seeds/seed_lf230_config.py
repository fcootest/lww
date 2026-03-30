"""Seed LF230 config data -- TNT transitions, TST_TRT, TST_Filter for Policy flow.

LF230 uses phase completion to move between L2 phases.
Only within-phase L3->L3 transitions use TNT.
"""

from src.modules.tnt.model import TNT
from src.modules.tnt.repository import tnt_repository
from src.modules.trt.model import TST_TRT
from src.modules.trt.repository import tst_trt_repository
from src.modules.filters.model import TSTFilter
from src.modules.filters.repository import tst_filter_repository


LF230_TNT_SEED = [
    # Within LF232 phase: L3 step transitions
    TNT(tnt_id="TNT-033", from_tst_id="TST-025", to_tst_id="TST-026", priority=1,
        condition_description="Check applicable laws"),
    TNT(tnt_id="TNT-034", from_tst_id="TST-026", to_tst_id="TST-027", priority=1,
        condition_description="Check compliance"),
    TNT(tnt_id="TNT-035", from_tst_id="TST-027", to_tst_id="TST-028", priority=1,
        condition_description="Check privacy"),
    TNT(tnt_id="TNT-036", from_tst_id="TST-028", to_tst_id="TST-029", priority=1,
        condition_description="Summarize policy review"),
]


def seed_all():
    """Seed LF230 config."""
    for tnt in LF230_TNT_SEED:
        if tnt_repository.get_by_id(tnt.tnt_id) is None:
            tnt_repository.create(tnt)

    # TST_TRT
    _trt_mappings = [
        ("TST-023", "TRT-001"),  # SUBMITTOR on LF231.1
        ("TST-025", "TRT-002"),  # LEGAL_APPROVER on LF232.1-5
        ("TST-026", "TRT-002"),
        ("TST-027", "TRT-002"),
        ("TST-028", "TRT-002"),
        ("TST-029", "TRT-002"),
        ("TST-031", "TRT-002"),  # LF233.1
        ("TST-033", "TRT-002"),  # LF234.1
    ]
    for tst_id, trt_id in _trt_mappings:
        if not tst_trt_repository.exists(tst_id, trt_id):
            tst_trt_repository.create(TST_TRT(tst_id=tst_id, trt_id=trt_id, is_required=True))

    # TST_Filter
    for ft in ["CTY", "PT", "LE", "TUT"]:
        if not tst_filter_repository.exists("TST-021", ft, ft):
            tst_filter_repository.create(TSTFilter(tst_id="TST-021", filter_type=ft, filter_code=ft))
