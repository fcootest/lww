"""My Tasks router -- user-specific task list API."""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error

router = APIRouter(
    prefix="/api/legal",
    tags=["My Tasks"],
)


@router.get("/my-tasks")
async def get_my_tasks(
    user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """Get current user tasks grouped by L1 root, showing latest status."""
    from src.modules.emp.repository import emp_repository
    from src.modules.tri.repository import tri_repository
    from src.modules.tsi.repository import tsi_repository
    from src.modules.tst.repository import tst_repository

    emp = emp_repository.get_by_code(user.get("emp_code", ""))
    if not emp:
        return send_error(message="Employee not found", status_code=400)

    # Find all TRI for this employee
    tri_list = tri_repository.get_by_emp(emp.emp_id)
    tsi_ids = [t.tsi_id for t in tri_list if t.tsi_id is not None]

    # Group by L1 root - show one entry per workflow with latest status
    seen_roots: dict[str, dict] = {}

    for tsi_id in tsi_ids:
        tsi = tsi_repository.get_by_id(tsi_id)
        if tsi is None:
            continue

        # Walk up to L1 root
        root_tsi = tsi
        while root_tsi.my_parent_task:
            parent = tsi_repository.get_by_id(root_tsi.my_parent_task)
            if parent is None:
                break
            root_tsi = parent

        root_id = root_tsi.tsi_id

        # Find the latest L3 status in this workflow (most recently updated)
        all_tsis = tsi_repository.get_all()
        all_l3s_in_tree = []
        # Collect L2 children of root
        l2s = [t for t in all_tsis if t.my_parent_task == root_id]
        for l2 in l2s:
            l3s = [t for t in all_tsis if t.my_parent_task == l2.tsi_id]
            all_l3s_in_tree.extend(l3s)

        # Find the last updated L3 (latest status)
        latest_status = root_tsi.status.value if hasattr(root_tsi.status, 'value') else root_tsi.status
        if all_l3s_in_tree:
            # Sort by updated_at descending, take the latest
            all_l3s_in_tree.sort(key=lambda t: t.updated_at, reverse=True)
            last_l3 = all_l3s_in_tree[0]
            last_l3_status = last_l3.status.value if hasattr(last_l3.status, 'value') else last_l3.status
            # Use the last L3 status as the display status
            latest_status = last_l3_status

        # Filter by status if provided
        if status and latest_status != status:
            continue

        # Skip if we already have this root (keep updating with latest)
        if root_id in seen_roots:
            # Update status if this one is newer
            seen_roots[root_id]["status"] = latest_status
            continue

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

        seen_roots[root_id] = {
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
