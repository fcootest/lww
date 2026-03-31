"""My Tasks router -- user-specific task list API."""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error

router = APIRouter(
    prefix="/api/legal",
    tags=["My Tasks"],
)


def _build_root_entry(root_tsi, all_tsis, emp_repository, tst_repository):
    """Build a task entry dict from an L1 root TSI."""
    root_id = root_tsi.tsi_id

    # Find the latest L3 status in this workflow
    all_l3s_in_tree = []
    l2s = [t for t in all_tsis if t.my_parent_task == root_id]
    for l2 in l2s:
        l3s = [t for t in all_tsis if t.my_parent_task == l2.tsi_id]
        all_l3s_in_tree.extend(l3s)

    latest_status = root_tsi.status.value if hasattr(root_tsi.status, 'value') else root_tsi.status
    if all_l3s_in_tree:
        all_l3s_in_tree.sort(key=lambda t: t.updated_at, reverse=True)
        last_l3 = all_l3s_in_tree[0]
        latest_status = last_l3.status.value if hasattr(last_l3.status, 'value') else last_l3.status

    # Get TST L1 name
    tst_l1_name = ""
    tst_l1 = tst_repository.get_by_id(root_tsi.tst_id)
    if tst_l1:
        tst_l1_name = tst_l1.tst_name

    # Get submitter name
    submitted_by_name = ""
    if root_tsi.requested_by:
        submitter = emp_repository.get_by_id(root_tsi.requested_by)
        if submitter:
            submitted_by_name = submitter.emp_name

    return {
        "tsi_id": root_tsi.tsi_id,
        "tsi_code": root_tsi.tsi_code,
        "title": root_tsi.title,
        "status": latest_status,
        "priority": root_tsi.priority.value if hasattr(root_tsi.priority, 'value') and root_tsi.priority else root_tsi.priority,
        "due_date": root_tsi.due_date,
        "assigned_to": root_tsi.assigned_to,
        "created_at": root_tsi.created_at.isoformat() if hasattr(root_tsi.created_at, 'isoformat') else str(root_tsi.created_at),
        "tst_l1_name": tst_l1_name,
        "submitted_by_name": submitted_by_name,
    }


@router.get("/my-tasks")
async def get_my_tasks(
    user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """Get current user tasks grouped by L1 root, showing latest status.
    
    SEC4 (Admin/Approver) sees ALL tasks.
    Other SECs see only tasks assigned to them via TRI.
    """
    from src.modules.emp.repository import emp_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tst.repository import tst_repository

    empsec = user.get("empsec", "")
    role_legal = user.get("role_legal", "")
    is_admin = empsec == "SEC4" or role_legal in ("Approver", "Checker")

    all_tsis = tsi_repository.get_all()
    seen_roots: dict[str, dict] = {}

    if is_admin:
        # SEC4/Approver: show ALL L1 root tasks
        root_tsis = [t for t in all_tsis if t.my_parent_task is None]
        for root_tsi in root_tsis:
            entry = _build_root_entry(root_tsi, all_tsis, emp_repository, tst_repository)
            if status and entry["status"] != status:
                continue
            seen_roots[root_tsi.tsi_id] = entry
    else:
        # Other SECs: show tasks where user is creator (requested_by) or assignee (assigned_to)
        emp_code = user.get("emp_code", "")
        # Also resolve emp_id for seed users (TRI compatibility)
        emp = emp_repository.get_by_code(emp_code)
        emp_id = emp.emp_id if emp else emp_code

        # Collect matching root TSIs: created by user OR assigned to user
        for tsi in all_tsis:
            if tsi.my_parent_task is not None:
                continue  # Skip non-root tasks

            requested_by = tsi.requested_by or ""
            assigned_to = tsi.assigned_to or ""

            is_mine = (
                requested_by in (emp_code, emp_id)
                or assigned_to in (emp_code, emp_id)
            )
            if not is_mine:
                continue

            root_id = tsi.tsi_id
            if root_id in seen_roots:
                continue

            entry = _build_root_entry(tsi, all_tsis, emp_repository, tst_repository)
            if status and entry["status"] != status:
                continue
            seen_roots[root_id] = entry

    tasks = list(seen_roots.values())

    # Pagination
    total = len(tasks)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = tasks[start:end]

    return send_success(data={
        "items": paginated,
        "total": total,
        "page": page,
        "page_size": page_size,
    })
