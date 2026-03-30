"""Seed LF240 config data -- TNT transitions, TST_TRT, TST_Filter for Contract flow.

LF240 relies on phase completion (not cross-phase TNTs) to move between L2 phases.
Only within-phase L3->L3 transitions are defined via TNT.
"""

from src.modules.tnt.model import TNT
from src.modules.tnt.repository import tnt_repository
from src.modules.trt.model import TST_TRT
from src.modules.trt.repository import tst_trt_repository
from src.modules.filters.model import TSTFilter
from src.modules.filters.repository import tst_filter_repository


LF240_TNT_SEED = [
    # Within LF242 phase: L3 step transitions
    TNT(tnt_id="TNT-060", from_tst_id="TST-038", to_tst_id="TST-039", priority=1,
        condition_description="After clause check, check laws"),
    TNT(tnt_id="TNT-061", from_tst_id="TST-039", to_tst_id="TST-040", priority=1,
        condition_description="After laws, check risks"),
    TNT(tnt_id="TNT-062", from_tst_id="TST-040", to_tst_id="TST-041", priority=1,
        condition_description="After risks, check compensation"),
    TNT(tnt_id="TNT-063", from_tst_id="TST-041", to_tst_id="TST-042", priority=1,
        condition_description="After compensation, summarize"),
]


def seed_all():
    """Seed LF240 config."""
    for tnt in LF240_TNT_SEED:
        if tnt_repository.get_by_id(tnt.tnt_id) is None:
            tnt_repository.create(tnt)

    # TST_TRT
    _trt_mappings = [
        ("TST-036", "TRT-001"),  # SUBMITTOR on LF241.1
        ("TST-038", "TRT-002"),  # LEGAL_APPROVER on review steps
        ("TST-039", "TRT-002"),
        ("TST-040", "TRT-002"),
        ("TST-041", "TRT-002"),
        ("TST-042", "TRT-002"),
        ("TST-044", "TRT-002"),  # LF243.1
        ("TST-046", "TRT-002"),  # LF244.1
        ("TST-048", "TRT-002"),  # LF245.1
        ("TST-050", "TRT-002"),  # LF246.1
        ("TST-052", "TRT-002"),  # LF247.1
    ]
    for tst_id, trt_id in _trt_mappings:
        if not tst_trt_repository.exists(tst_id, trt_id):
            tst_trt_repository.create(TST_TRT(tst_id=tst_id, trt_id=trt_id, is_required=True))

    # TST_Filter
    for ft in ["CTY", "PT", "LE", "TUT"]:
        if not tst_filter_repository.exists("TST-034", ft, ft):
            tst_filter_repository.create(TSTFilter(tst_id="TST-034", filter_type=ft, filter_code=ft))
