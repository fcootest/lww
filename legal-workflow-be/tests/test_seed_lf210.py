"""Tests for Step 28: LF210 Copyright seed config data."""

import pytest


@pytest.fixture(autouse=True)
def seed_all_data():
    """Ensure all repositories are seeded before each test."""
    from src.seeds.seed_tst import seed_all as seed_tst
    from src.seeds.seed_tnt import seed_all as seed_tnt
    from src.seeds.seed_emp import seed_all as seed_emp
    from src.seeds.seed_tst_trt import seed_all as seed_tst_trt
    from src.seeds.seed_tri import seed_all as seed_tri
    from src.seeds.seed_lf210_config import seed_all as seed_lf210_config

    seed_tst()
    seed_tnt()
    seed_emp()
    seed_tst_trt()
    seed_tri()
    seed_lf210_config()
    yield


def test_tst_9_rows():
    """9 TST rows exist for LF210 after seed."""
    from src.modules.tst.repository import tst_repository
    lf210_tsts = [t for t in tst_repository.get_all() if t.tst_code.startswith("LF21")]
    # LF210, LF211, LF211.1, LF212, LF212.1..LF212.5 = 9
    assert len(lf210_tsts) == 9


def test_tnt_8_rows():
    """8 TNT rows exist for LF210 transitions."""
    from src.modules.tnt.repository import tnt_repository
    all_tnt = tnt_repository.get_all()
    lf210_tnt = [t for t in all_tnt if t.tnt_id.startswith("TNT-00")]
    assert len(lf210_tnt) == 8


def test_tst_trt_submittor_on_lf211_1():
    """TST_TRT: SUBMITTOR mapped to LF211.1 (TST-003)."""
    from src.modules.trt.repository import tst_trt_repository
    mappings = tst_trt_repository.get_by_tst("TST-003")
    trt_ids = [m.trt_id for m in mappings]
    assert "TRT-001" in trt_ids  # TRT-001 = SUBMITTOR


def test_tst_trt_legal_approver_on_lf212_1():
    """TST_TRT: LEGAL_APPROVER mapped to LF212.1 (TST-005)."""
    from src.modules.trt.repository import tst_trt_repository
    mappings = tst_trt_repository.get_by_tst("TST-005")
    trt_ids = [m.trt_id for m in mappings]
    assert "TRT-002" in trt_ids  # TRT-002 = LEGAL_APPROVER


def test_tst_filter_4_on_lf210():
    """TST_Filter: 4 filters on LF210 (TST-001)."""
    from src.modules.filters.repository import tst_filter_repository
    filters = tst_filter_repository.get_by_tst("TST-001")
    assert len(filters) >= 4
    filter_types = {f.filter_type for f in filters}
    assert {"CTY", "PT", "LE", "TUT"}.issubset(filter_types)
