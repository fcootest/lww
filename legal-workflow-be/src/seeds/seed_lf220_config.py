"""Seed LF220 config data -- TNT transitions, TST_TRT, TST_TDT, TST_Filter for Trademark flow."""

from src.modules.tnt.model import TNT
from src.modules.tnt.repository import tnt_repository
from src.modules.trt.model import TST_TRT
from src.modules.trt.repository import tst_trt_repository
from src.modules.filters.model import TSTFilter
from src.modules.filters.repository import tst_filter_repository


LF220_TNT_SEED = [
    # Within LF221 phase: L2 -> first L3
    TNT(tnt_id="TNT-020", from_tst_id="TST-011", to_tst_id="TST-012", priority=1,
        condition_description="Start trademark input"),
    # L3 -> L2 phase transition (via TNT, engine creates L3 under current L2)
    TNT(tnt_id="TNT-021", from_tst_id="TST-012", to_tst_id="TST-013", priority=1,
        condition_description="After input, start trademark review"),
    # Within LF222 phase
    TNT(tnt_id="TNT-022", from_tst_id="TST-013", to_tst_id="TST-014", priority=1,
        condition_description="Start WIPO search"),
    TNT(tnt_id="TNT-023", from_tst_id="TST-014", to_tst_id="TST-015", priority=1,
        condition_description="After WIPO, search USPTO"),
    TNT(tnt_id="TNT-024", from_tst_id="TST-015", to_tst_id="TST-016", priority=1,
        condition_description="After USPTO, search VN IP"),
    TNT(tnt_id="TNT-025", from_tst_id="TST-016", to_tst_id="TST-017", priority=1,
        condition_description="After VN IP, Google search"),
    TNT(tnt_id="TNT-026", from_tst_id="TST-017", to_tst_id="TST-018", priority=1,
        condition_description="After Google, WIPO Image"),
    TNT(tnt_id="TNT-027", from_tst_id="TST-018", to_tst_id="TST-019", priority=1,
        condition_description="After WIPO Image, reverse image"),
    TNT(tnt_id="TNT-028", from_tst_id="TST-019", to_tst_id="TST-020", priority=1,
        condition_description="After reverse image, summarize"),
]


def seed_all():
    """Seed LF220 config: TNT, TST_TRT, TST_Filter."""
    # TNT transitions
    for tnt in LF220_TNT_SEED:
        if tnt_repository.get_by_id(tnt.tnt_id) is None:
            tnt_repository.create(tnt)

    # TST_TRT: SUBMITTOR on LF221.1 (TST-012), LEGAL_APPROVER on LF222.1-7 (TST-014..TST-020)
    _trt_mappings = [
        ("TST-012", "TRT-001"),  # SUBMITTOR
        ("TST-014", "TRT-002"),  # LEGAL_APPROVER
        ("TST-015", "TRT-002"),
        ("TST-016", "TRT-002"),
        ("TST-017", "TRT-002"),
        ("TST-018", "TRT-002"),
        ("TST-019", "TRT-002"),
        ("TST-020", "TRT-002"),
    ]
    for tst_id, trt_id in _trt_mappings:
        if not tst_trt_repository.exists(tst_id, trt_id):
            tst_trt_repository.create(TST_TRT(tst_id=tst_id, trt_id=trt_id, is_required=True))

    # TST_Filter: filter types on LF220 (TST-010)
    _filter_configs = [
        ("TST-010", "CTY", "CTY"),
        ("TST-010", "PT", "PT"),
        ("TST-010", "LE", "LE"),
        ("TST-010", "TUT", "TUT"),
    ]
    for tst_id, ft, fc in _filter_configs:
        if not tst_filter_repository.exists(tst_id, ft, fc):
            tst_filter_repository.create(TSTFilter(tst_id=tst_id, filter_type=ft, filter_code=fc))
