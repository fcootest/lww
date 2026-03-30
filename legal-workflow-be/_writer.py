import pathlib

content = (
    '"""Workflow engine -- auto-navigate TST tree to create TSI L2 + L3."""\n'
    '\n'
    'from uuid import uuid4\n'
    'from src.modules.tsi.model import TSI, TSIStatus\n'
    'from src.modules.tsi.repository import tsi_repository\n'
    'from src.modules.tsi.service import _generate_tsi_code\n'
    'from src.modules.tsi_filter.model import TSIFilter\n'
    'from src.modules.tsi_filter.repository import tsi_filter_repository\n'
    'from src.modules.tst.repository import tst_repository\n'
    'from src.modules.tsev.model import TSEV, TSEVEventType\n'
    'from src.modules.tsev.repository import tsev_repository\n'
)

pathlib.Path("src/modules/workflow/engine.py").write_text(content)
print("test write OK")
