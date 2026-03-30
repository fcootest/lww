"""Seed LF210 config data — TST_TRT, TST_TDT, TST_Filter, and TDT for Copyright flow."""

from src.modules.trt.model import TST_TRT
from src.modules.trt.repository import tst_trt_repository
from src.modules.filters.model import TSTFilter, TSTTDT
from src.modules.filters.repository import tst_filter_repository, tst_tdt_repository
from src.modules.tdt.model import TDT
from src.modules.tdt.repository import tdt_repository


def seed_all():
    """Seed LF210 config: TST_TRT, TST_TDT, TST_Filter, TDT."""

    # --- TDT: document types ---
    if tdt_repository.get_by_id("TDT-001") is None:
        tdt_repository.create(TDT(
            tdt_id="TDT-001", tdt_code="UI_COMPARISON",
            tdt_name="UI Comparison Document",
            description="Ban so sanh UI/UX",
            file_extensions=".pdf,.docx,.png,.jpg",
            is_required=True,
        ))
    if tdt_repository.get_by_id("TDT-004") is None:
        tdt_repository.create(TDT(
            tdt_id="TDT-004", tdt_code="COPYRIGHT_REPORT",
            tdt_name="Copyright Review Report",
            description="Bao cao tong hop ket qua ra soat ban quyen",
            file_extensions=".pdf,.docx",
            is_required=True,
        ))

    # --- TST_TRT: role mappings for LF210 ---
    _trt_mappings = [
        # SUBMITTOR on LF211.1 (TST-003)
        ("TST-003", "TRT-001"),
        # LEGAL_APPROVER on LF212.1-5 (TST-005..TST-009)
        ("TST-005", "TRT-002"),
        ("TST-006", "TRT-002"),
        ("TST-007", "TRT-002"),
        ("TST-008", "TRT-002"),
        ("TST-009", "TRT-002"),
    ]
    for tst_id, trt_id in _trt_mappings:
        if not tst_trt_repository.exists(tst_id, trt_id):
            tst_trt_repository.create(TST_TRT(tst_id=tst_id, trt_id=trt_id, is_required=True))

    # --- TST_TDT: document type mappings ---
    _tdt_mappings = [
        ("TST-003", "TDT-001", True),   # UI_COMPARISON required on LF211.1
        ("TST-009", "TDT-004", True),   # COPYRIGHT_REPORT required on LF212.5
    ]
    for tst_id, tdt_id, is_req in _tdt_mappings:
        if not tst_tdt_repository.exists(tst_id, tdt_id):
            tst_tdt_repository.create(TSTTDT(tst_id=tst_id, tdt_id=tdt_id, is_required=is_req))

    # --- TST_Filter: filter types applicable to LF210 ---
    _filter_configs = [
        ("TST-001", "CTY", "CTY"),
        ("TST-001", "PT", "PT"),
        ("TST-001", "LE", "LE"),
        ("TST-001", "TUT", "TUT"),
    ]
    for tst_id, filter_type, filter_code in _filter_configs:
        if not tst_filter_repository.exists(tst_id, filter_type, filter_code):
            tst_filter_repository.create(TSTFilter(
                tst_id=tst_id,
                filter_type=filter_type,
                filter_code=filter_code,
            ))
