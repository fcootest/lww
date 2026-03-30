"""TSI router -- task creation and management APIs."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error
from src.modules.tsi.schema import TSICreateRequest
from src.modules.tsi.service import create_task_l1

router = APIRouter(
    prefix="/api/legal/task",
    tags=["TSI Task"],
)


@router.post("/")
async def create_task(req: TSICreateRequest, user: dict = Depends(get_current_user)):
    """Create a new Level 1 task."""
    try:
        tsi = create_task_l1(req, emp_code=user.get("emp_code", "SYSTEM"))
        return send_success(
            data=tsi.model_dump(mode="json"),
            message="Task created",
            status_code=201,
        )
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


@router.post("/{tsi_id}/approve")
async def approve_task(tsi_id: str, user: dict = Depends(get_current_user)):
    """Approve (complete) a TSI L3 task and trigger next step."""
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.tsev.model import TSEV, TSEVEventType
    from src.modules.tsev.repository import tsev_repository
    from src.common.status_machine import assert_transition
    from src.modules.workflow.engine import find_and_create_next_step
    from uuid import uuid4

    tsi = tsi_repository.get_by_id(tsi_id)
    if not tsi:
        return send_error(message="TSI not found", status_code=404)

    # Check user is assigned
    emp = emp_repository.get_by_code(user.get("emp_code", ""))
    if not emp:
        return send_error(message="Employee not found", status_code=400)

    assignments = tri_repository.get_by_tsi(tsi_id)
    assigned_emp_ids = [a.emp_id for a in assignments]
    if emp.emp_id not in assigned_emp_ids:
        return send_error(message="You are not assigned to this task", status_code=403)

    # Auto-transition PENDING -> IN_PROGRESS if needed
    current_status = tsi.status.value if hasattr(tsi.status, 'value') else tsi.status
    if current_status == 'PENDING':
        tsi_repository.update(tsi_id, {'status': 'IN_PROGRESS'})
        current_status = 'IN_PROGRESS'

    # Determine if user is admin (Legal Manager) or regular user
    # Admin = LEGAL_MANAGER role or ADMIN role with TiepTA code
    is_admin = user.get("role") in ("LEGAL_MANAGER", "ADMIN")

    if is_admin:
        # Admin approve -> APPROVED, trigger next step
        try:
            assert_transition(current_status, 'APPROVED')
        except ValueError:
            # If already SUBMITTED, transition SUBMITTED->APPROVED
            from src.common.status_machine import is_valid_transition
            if not is_valid_transition(current_status, 'APPROVED'):
                return send_error(message=f"Cannot approve from {current_status}", status_code=400)

        tsi_repository.update(tsi_id, {'status': 'APPROVED'})
        tsev = TSEV(
            tsev_id=f"TSEV-{uuid4().hex[:8]}",
            tsi_id=tsi_id,
            event_type=TSEVEventType.APPROVE,
            emp_id=emp.emp_id,
        )
        tsev_repository.create(tsev)

        # Trigger next step
        updated_tsi = tsi_repository.get_by_id(tsi_id)
        find_and_create_next_step(updated_tsi)
    else:
        # User submit -> SUBMITTED (waiting for admin review)
        new_status = 'SUBMITTED'
        tsi_repository.update(tsi_id, {'status': new_status})
        tsev = TSEV(
            tsev_id=f"TSEV-{uuid4().hex[:8]}",
            tsi_id=tsi_id,
            event_type=TSEVEventType.UPDATE,
            emp_id=emp.emp_id,
            event_data='{"action": "submit_to_review"}',
        )
        tsev_repository.create(tsev)
        updated_tsi = tsi_repository.get_by_id(tsi_id)

    return send_success(
        data=updated_tsi.model_dump(mode="json"),
        message="Task approved",
    )


@router.post("/{tsi_id}/reject")
async def reject_task(tsi_id: str, req: RejectRequest, user: dict = Depends(get_current_user)):
    """Reject a TSI task."""
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.emp.repository import emp_repository
    from src.modules.tsev.model import TSEV, TSEVEventType
    from src.modules.tsev.repository import tsev_repository
    from src.common.status_machine import assert_transition
    from uuid import uuid4
    import json

    tsi = tsi_repository.get_by_id(tsi_id)
    if not tsi:
        return send_error(message="TSI not found", status_code=404)

    emp = emp_repository.get_by_code(user.get("emp_code", ""))
    if not emp:
        return send_error(message="Employee not found", status_code=400)

    assignments = tri_repository.get_by_tsi(tsi_id)
    assigned_emp_ids = [a.emp_id for a in assignments]
    if emp.emp_id not in assigned_emp_ids:
        return send_error(message="You are not assigned to this task", status_code=403)

    # Auto-transition PENDING -> IN_PROGRESS if needed
    current_status = tsi.status.value if hasattr(tsi.status, 'value') else tsi.status
    if current_status == 'PENDING':
        tsi_repository.update(tsi_id, {'status': 'IN_PROGRESS'})
        current_status = 'IN_PROGRESS'

    try:
        assert_transition(current_status, "REJECTED")
    except ValueError as e:
        return send_error(message=str(e), status_code=400)

    tsi_repository.update(tsi_id, {"status": "REJECTED"})

    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=TSEVEventType.REJECT,
        emp_id=emp.emp_id,
        event_data=json.dumps({"reason": req.reason}),
    )
    tsev_repository.create(tsev)

    # Trigger next step even after reject (workflow continues)
    from src.modules.workflow.engine import find_and_create_next_step
    updated_tsi = tsi_repository.get_by_id(tsi_id)
    find_and_create_next_step(updated_tsi)

    return send_success(
        data=updated_tsi.model_dump(mode="json"),
        message="Task rejected",
    )


@router.get("/{tsi_id}")
async def get_task_detail(tsi_id: str, user: dict = Depends(get_current_user)):
    """Get detailed task information including progress, documents, events."""
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tst.repository import tst_repository
    from src.modules.tsev.repository import tsev_repository
    from src.modules.tdi.repository import tdi_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tsi_filter.repository import tsi_filter_repository

    tsi = tsi_repository.get_by_id(tsi_id)
    if not tsi:
        return send_error(message="TSI not found", status_code=404)

    # Build progress tree
    progress = _build_progress_tree(tsi, tsi_repository, tst_repository)

    # Collect all TSI IDs in the tree (L1 + L2 + L3) for aggregation
    all_tree_ids = _collect_tree_tsi_ids(tsi, tsi_repository)

    # Get documents aggregated from entire tree
    documents = [d.model_dump(mode="json") for d in tdi_repository.get_by_tsi_ids(all_tree_ids)]

    # Get events aggregated from entire tree, ordered by created_at
    events = tsev_repository.get_by_tsi_ids(all_tree_ids)
    events.sort(key=lambda e: e.created_at)
    events_data = [e.model_dump(mode="json") for e in events]

    # Get assignments aggregated from entire tree
    all_assignments = []
    for tid in all_tree_ids:
        all_assignments.extend(tri_repository.get_by_tsi(tid))
    assignments = [a.model_dump(mode="json") for a in all_assignments]

    # Get filters
    filters = [f.model_dump(mode="json") for f in tsi_filter_repository.get_by_tsi(tsi_id)]

    return send_success(data={
        "tsi": tsi.model_dump(mode="json"),
        "progress": progress,
        "documents": documents,
        "events": events_data,
        "assignments": assignments,
        "filters": filters,
    })


def _collect_tree_tsi_ids(tsi, tsi_repository) -> list[str]:
    """Collect all TSI IDs in the tree (root L1 + all L2 + all L3)."""
    all_tsis = tsi_repository.get_all()

    # Find root L1
    root = tsi
    while root.my_parent_task:
        parent = tsi_repository.get_by_id(root.my_parent_task)
        if parent is None:
            break
        root = parent

    ids = [root.tsi_id]

    # L2 children
    l2_tsis = [t for t in all_tsis if t.my_parent_task == root.tsi_id]
    for l2 in l2_tsis:
        ids.append(l2.tsi_id)
        # L3 children
        l3_tsis = [t for t in all_tsis if t.my_parent_task == l2.tsi_id]
        for l3 in l3_tsis:
            ids.append(l3.tsi_id)

    return ids


def _build_progress_tree(tsi, tsi_repository, tst_repository):
    """Build TST tree progress showing status for each node."""
    all_tsis = tsi_repository.get_all()

    # Find root L1
    root = tsi
    while root.my_parent_task:
        parent = tsi_repository.get_by_id(root.my_parent_task)
        if parent is None:
            break
        root = parent

    progress = []

    # L1
    tst_l1 = tst_repository.get_by_id(root.tst_id)
    l1_node = {
        "tsi_id": root.tsi_id,
        "tst_id": root.tst_id,
        "tst_name": tst_l1.tst_name if tst_l1 else "Unknown",
        "tst_level": 1,
        "status": root.status.value,
        "children": [],
    }

    # Find L2 children
    l2_tsis = [t for t in all_tsis if t.my_parent_task == root.tsi_id]
    for l2 in l2_tsis:
        tst_l2 = tst_repository.get_by_id(l2.tst_id)
        l2_node = {
            "tsi_id": l2.tsi_id,
            "tst_id": l2.tst_id,
            "tst_name": tst_l2.tst_name if tst_l2 else "Unknown",
            "tst_level": 2,
            "status": l2.status.value,
            "children": [],
        }

        # Find L3 children
        l3_tsis = [t for t in all_tsis if t.my_parent_task == l2.tsi_id]
        for l3 in l3_tsis:
            tst_l3 = tst_repository.get_by_id(l3.tst_id)
            # Get latest comment/feedback for this L3
            from src.modules.tsev.repository import tsev_repository
            l3_events = tsev_repository.get_by_tsi(l3.tsi_id)
            l3_comment = ""
            for ev in reversed(l3_events):
                if ev.emp_id == "AI_REVIEWER":
                    continue  # Skip AI events, only show human comments
                evt = ev.event_type.value if hasattr(ev.event_type, 'value') else ev.event_type
                if evt == "COMMENT" and ev.event_data:
                    l3_comment = ev.event_data
                    break
                if evt == "REJECT" and ev.event_data:
                    import json
                    try:
                        d = json.loads(ev.event_data)
                        l3_comment = d.get("reason", ev.event_data)
                    except Exception:
                        l3_comment = ev.event_data
                    break

            # Get AI review result for this L3
            ai_review = None
            for ev in reversed(l3_events):
                if ev.emp_id == "AI_REVIEWER" and ev.event_data:
                    try:
                        ai_review = json.loads(ev.event_data)
                    except Exception:
                        pass
                    break

            # If no human comment but AI review exists, show AI score as comment
            display_comment = l3_comment
            if not display_comment and ai_review:
                verdict = ai_review.get("verdict", "")
                score = ai_review.get("score", 0)
                summary = ai_review.get("summary", "")
                display_comment = f"AI: {verdict} ({score}%) - {summary}"

            l3_node = {
                "tsi_id": l3.tsi_id,
                "tst_id": l3.tst_id,
                "tst_name": tst_l3.tst_name if tst_l3 else "Unknown",
                "tst_level": 3,
                "status": l3.status.value,
                "comment": display_comment,
                "ai_review": ai_review,
            }
            l2_node["children"].append(l3_node)

        l1_node["children"].append(l2_node)

    progress.append(l1_node)
    return progress
