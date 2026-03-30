"""Workflow engine -- auto-navigate TST tree to create TSI L2 + L3."""

from uuid import uuid4
from src.modules.tsi.model import TSI, TSIStatus
from src.modules.tsi.repository import tsi_repository
from src.modules.tsi.service import _generate_tsi_code
from src.modules.tsi_filter.model import TSIFilter
from src.modules.tsi_filter.repository import tsi_filter_repository
from src.modules.tst.repository import tst_repository
from src.modules.tsev.model import TSEV, TSEVEventType
from src.modules.tsev.repository import tsev_repository


def navigate_and_create_first_step(tsi_l1: TSI):
    """Navigate from TSI L1 down the TST tree to create TSI L2 and TSI L3."""
    tst_l1 = tst_repository.get_by_id(tsi_l1.tst_id)
    if not tst_l1:
        return

    l2_children = tst_repository.get_children(tst_l1.tst_id)
    l2_children.sort(key=lambda x: x.tst_code)
    if not l2_children:
        return

    first_l2 = l2_children[0]

    tsi_l2_id = f"TSI-{uuid4().hex[:8]}"
    tsi_l2 = TSI(
        tsi_id=tsi_l2_id,
        tsi_code=_generate_tsi_code(),
        tst_id=first_l2.tst_id,
        my_parent_task=tsi_l1.tsi_id,
        title=f"{tsi_l1.title} - {first_l2.tst_name}",
        status=TSIStatus.IN_PROGRESS,
        priority=tsi_l1.priority,
        current_tst_level=2,
        current_tst_id=first_l2.tst_id,
    )
    tsi_repository.create(tsi_l2)

    l3_children = tst_repository.get_children(first_l2.tst_id)
    l3_children.sort(key=lambda x: x.tst_code)
    if not l3_children:
        return

    first_l3 = l3_children[0]

    tsi_l3_id = f"TSI-{uuid4().hex[:8]}"
    tsi_l3 = TSI(
        tsi_id=tsi_l3_id,
        tsi_code=_generate_tsi_code(),
        tst_id=first_l3.tst_id,
        my_parent_task=tsi_l2.tsi_id,
        title=f"{tsi_l1.title} - {first_l3.tst_name}",
        status=TSIStatus.PENDING,
        priority=tsi_l1.priority,
        current_tst_level=3,
        current_tst_id=first_l3.tst_id,
    )
    tsi_repository.create(tsi_l3)

    l1_filters = tsi_filter_repository.get_by_tsi(tsi_l1.tsi_id)
    for f in l1_filters:
        f2 = TSIFilter(
            id=tsi_filter_repository.next_id(),
            tsi_id=tsi_l2_id,
            filter_type=f.filter_type,
            filter_code=f.filter_code,
        )
        tsi_filter_repository.create(f2)
        f3 = TSIFilter(
            id=tsi_filter_repository.next_id(),
            tsi_id=tsi_l3_id,
            filter_type=f.filter_type,
            filter_code=f.filter_code,
        )
        tsi_filter_repository.create(f3)

    from src.modules.workflow.assignment import assign_handler
    assign_handler(tsi_l3)


def _create_tsi_l3(tst_l3, parent_tsi_l2, root_tsi_l1):
    """Helper: Create a TSI L3 from a TST L3 under a given L2 parent."""
    tsi_l3_id = f"TSI-{uuid4().hex[:8]}"
    tsi_l3 = TSI(
        tsi_id=tsi_l3_id,
        tsi_code=_generate_tsi_code(),
        tst_id=tst_l3.tst_id,
        my_parent_task=parent_tsi_l2.tsi_id,
        title=f"{root_tsi_l1.title} - {tst_l3.tst_name}",
        status=TSIStatus.PENDING,
        priority=root_tsi_l1.priority,
        current_tst_level=3,
        current_tst_id=tst_l3.tst_id,
    )
    tsi_repository.create(tsi_l3)

    l1_filters = tsi_filter_repository.get_by_tsi(root_tsi_l1.tsi_id)
    for f in l1_filters:
        filt = TSIFilter(
            id=tsi_filter_repository.next_id(),
            tsi_id=tsi_l3_id,
            filter_type=f.filter_type,
            filter_code=f.filter_code,
        )
        tsi_filter_repository.create(filt)

    from src.modules.workflow.assignment import assign_handler
    assign_handler(tsi_l3)

    return tsi_l3


def _create_tsi_l2_with_first_l3(tst_l2, parent_tsi_l1):
    """Helper: Create a TSI L2 and its first L3 child."""
    tsi_l2_id = f"TSI-{uuid4().hex[:8]}"
    tsi_l2 = TSI(
        tsi_id=tsi_l2_id,
        tsi_code=_generate_tsi_code(),
        tst_id=tst_l2.tst_id,
        my_parent_task=parent_tsi_l1.tsi_id,
        title=f"{parent_tsi_l1.title} - {tst_l2.tst_name}",
        status=TSIStatus.IN_PROGRESS,
        priority=parent_tsi_l1.priority,
        current_tst_level=2,
        current_tst_id=tst_l2.tst_id,
    )
    tsi_repository.create(tsi_l2)

    l1_filters = tsi_filter_repository.get_by_tsi(parent_tsi_l1.tsi_id)
    for f in l1_filters:
        filt = TSIFilter(
            id=tsi_filter_repository.next_id(),
            tsi_id=tsi_l2_id,
            filter_type=f.filter_type,
            filter_code=f.filter_code,
        )
        tsi_filter_repository.create(filt)

    l3_children = tst_repository.get_children(tst_l2.tst_id)
    l3_children.sort(key=lambda x: x.tst_code)
    if l3_children:
        _create_tsi_l3(l3_children[0], tsi_l2, parent_tsi_l1)

    return tsi_l2


def _get_root_tsi_l1(tsi):
    """Walk up the parent chain to find the root TSI L1."""
    current = tsi
    while current.my_parent_task:
        parent = tsi_repository.get_by_id(current.my_parent_task)
        if parent is None:
            break
        current = parent
    return current


def find_and_create_next_step(tsi_completed):
    """After a TSI L3 is completed, find the next step via TNT transitions."""
    from src.modules.tnt.repository import tnt_repository

    tst_current = tst_repository.get_by_id(tsi_completed.tst_id)
    if not tst_current:
        return

    transitions = tnt_repository.get_all(from_tst_id=tst_current.tst_id)
    transitions.sort(key=lambda t: t.priority or 999)

    matched_tnt = None
    for tnt in transitions:
        if tnt.condition_expression is None:
            matched_tnt = tnt
            break
        try:
            from src.modules.workflow.condition_evaluator import evaluate_condition
            if evaluate_condition(tnt.condition_expression, {}):
                matched_tnt = tnt
                break
        except (ImportError, Exception):
            continue

    if matched_tnt:
        to_tst = tst_repository.get_by_id(matched_tnt.to_tst_id)
        if not to_tst:
            return

        root_l1 = _get_root_tsi_l1(tsi_completed)

        # Check: is the target TST a L2 (phase change) or L3 (same phase step)?
        if to_tst.tst_level == 2:
            # Phase transition: complete current L2, create new L2 + first L3
            parent_l2 = tsi_repository.get_by_id(tsi_completed.my_parent_task)
            if parent_l2:
                tsi_repository.update(parent_l2.tsi_id, {"status": TSIStatus.COMPLETED.value})
            _create_tsi_l2_with_first_l3(to_tst, root_l1)
        elif to_tst.tst_level == 3:
            # Same phase, next step
            parent_l2 = tsi_repository.get_by_id(tsi_completed.my_parent_task)
            if not parent_l2:
                return
            _create_tsi_l3(to_tst, parent_l2, root_l1)
        else:
            # L1 target - unusual, skip
            pass
    else:
        handle_phase_completion(tsi_completed)


def handle_phase_completion(tsi_completed):
    """Handle phase completion when no more TNT transitions exist for L3."""
    parent_l2 = tsi_repository.get_by_id(tsi_completed.my_parent_task)
    if not parent_l2:
        return

    all_tsis = tsi_repository.get_all()
    sibling_l3s = [t for t in all_tsis if t.my_parent_task == parent_l2.tsi_id]

    all_done = all(t.status in (TSIStatus.COMPLETED, TSIStatus.APPROVED, TSIStatus.REJECTED) for t in sibling_l3s)
    if not all_done:
        return

    any_rejected = any(t.status == TSIStatus.REJECTED for t in sibling_l3s)
    phase_status = TSIStatus.REJECTED.value if any_rejected else TSIStatus.COMPLETED.value
    tsi_repository.update(parent_l2.tsi_id, {"status": phase_status})

    root_l1 = _get_root_tsi_l1(tsi_completed)

    tst_l1 = tst_repository.get_by_id(root_l1.tst_id)
    if not tst_l1:
        return

    l2_tst_children = tst_repository.get_children(tst_l1.tst_id)
    l2_tst_children.sort(key=lambda x: x.tst_code)

    instantiated_tst_ids = set()
    for t in all_tsis:
        if t.my_parent_task == root_l1.tsi_id and t.current_tst_level == 2:
            instantiated_tst_ids.add(t.tst_id)

    next_l2_tst = None
    for tst_l2 in l2_tst_children:
        if tst_l2.tst_id not in instantiated_tst_ids:
            next_l2_tst = tst_l2
            break

    if next_l2_tst:
        _create_tsi_l2_with_first_l3(next_l2_tst, root_l1)
    else:
        tsi_repository.update(root_l1.tsi_id, {"status": TSIStatus.COMPLETED.value})

        import json
        wf_msg = json.dumps({"message": "Workflow completed"})
        tsev = TSEV(
            tsev_id=f"TSEV-{uuid4().hex[:8]}",
            tsi_id=root_l1.tsi_id,
            event_type=TSEVEventType.UPDATE,
            emp_id="SYSTEM",
            event_data=wf_msg,
        )
        tsev_repository.create(tsev)
