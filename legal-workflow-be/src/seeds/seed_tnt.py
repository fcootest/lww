"""Seed TNT data — transitions for LF210 Copyright Check flow."""

from src.modules.tnt.model import TNT
from src.modules.tnt.repository import tnt_repository


LF210_TNT_SEED = [
    TNT(tnt_id="TNT-001", from_tst_id="TST-002", to_tst_id="TST-003", priority=1,
        condition_description="After input, prepare comparison"),
    TNT(tnt_id="TNT-002", from_tst_id="TST-003", to_tst_id="TST-004", priority=1,
        condition_description="After preparation, start review"),
    TNT(tnt_id="TNT-003", from_tst_id="TST-004", to_tst_id="TST-005", priority=1,
        condition_description="Start screen comparison"),
    TNT(tnt_id="TNT-004", from_tst_id="TST-005", to_tst_id="TST-006", priority=2,
        condition_description="After screen check, check assets"),
    TNT(tnt_id="TNT-005", from_tst_id="TST-006", to_tst_id="TST-007", priority=3,
        condition_description="After asset check, check AI images"),
    TNT(tnt_id="TNT-006", from_tst_id="TST-007", to_tst_id="TST-008", priority=4,
        condition_description="After AI check, check store policy"),
    TNT(tnt_id="TNT-007", from_tst_id="TST-008", to_tst_id="TST-009", priority=5,
        condition_description="After policy check, summarize"),
    TNT(tnt_id="TNT-008", from_tst_id="TST-002", to_tst_id="TST-004", priority=2,
        condition_expression='{"skip_preparation": true}',
        condition_description="Skip preparation if already done"),
]


def seed_all():
    """Seed all TNT data."""
    tnt_repository.seed(LF210_TNT_SEED)
