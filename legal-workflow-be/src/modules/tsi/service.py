"""TSI service — business logic for task creation."""

from uuid import uuid4
from datetime import datetime
from src.modules.tsi.model import TSI, TSIStatus, TSIPriority
from src.modules.tsi.repository import tsi_repository
from src.modules.tsi.schema import TSICreateRequest
from src.modules.tsi_filter.model import TSIFilter
from src.modules.tsi_filter.repository import tsi_filter_repository
from src.modules.tsev.model import TSEV, TSEVEventType
from src.modules.tsev.repository import tsev_repository
from src.modules.tst.repository import tst_repository


def _generate_tsi_code() -> str:
    """Generate TSI code in format TSI-YYYYMMDD-NNN."""
    counter = tsi_repository.next_counter()
    date_str = datetime.utcnow().strftime("%Y%m%d")
    return f"TSI-{date_str}-{counter:03d}"


def create_task_l1(req: TSICreateRequest, emp_code: str) -> TSI:
    """Create a Level 1 task instance.

    Validates that tst_id refers to a Level 1 TST.
    Creates TSI, TSI_Filter rows, and TSEV CREATE event.
    Then triggers auto-navigation to create L2+L3.
    """
    # Validate tst_id exists and is Level 1
    tst = tst_repository.get_by_id(req.tst_id)
    if tst is None:
        raise ValueError(f"TST '{req.tst_id}' not found")
    if tst.tst_level != 1:
        raise ValueError(f"TST '{req.tst_id}' is level {tst.tst_level}, expected level 1")

    # Create TSI L1
    tsi_id = f"TSI-{uuid4().hex[:8]}"
    tsi_code = _generate_tsi_code()

    priority = None
    if req.priority:
        priority = TSIPriority(req.priority)

    # Resolve emp_code to emp_id for requested_by
    from src.modules.emp.repository import emp_repository
    emp = emp_repository.get_by_code(emp_code)
    emp_id = emp.emp_id if emp else emp_code

    tsi = TSI(
        tsi_id=tsi_id,
        tsi_code=tsi_code,
        tst_id=req.tst_id,
        title=req.title,
        description=req.description,
        status=TSIStatus.IN_PROGRESS,
        priority=priority,
        requested_by=emp_id,
        due_date=req.due_date,
        current_tst_level=1,
        current_tst_id=req.tst_id,
    )
    tsi_repository.create(tsi)

    # Save TSI_Filter rows
    for f in req.filters:
        filt = TSIFilter(
            id=tsi_filter_repository.next_id(),
            tsi_id=tsi_id,
            filter_type=f.filter_type,
            filter_code=f.filter_code,
        )
        tsi_filter_repository.create(filt)

    # Create TSEV(CREATE) event
    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=TSEVEventType.CREATE,
        emp_id=emp_code,
    )
    tsev_repository.create(tsev)

    # Auto-navigate to create L2 + L3
    from src.modules.workflow.engine import navigate_and_create_first_step
    navigate_and_create_first_step(tsi)

    return tsi


tsi_service = None  # not needed as standalone singleton; functions used directly
