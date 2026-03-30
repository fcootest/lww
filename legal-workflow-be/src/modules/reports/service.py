"""Reports service -- SLA and Workload statistics."""

from datetime import datetime
from src.modules.tsi.repository import tsi_repository
from src.modules.tri.repository import tri_repository
from src.modules.tst.repository import tst_repository
from src.modules.emp.repository import emp_repository


def get_sla_report():
    """Get SLA compliance report grouped by L1 task type.

    Returns on_time count, late count, sla_compliance_rate per TST L1.
    """
    all_tsis = tsi_repository.get_all()
    l1_tsis = [t for t in all_tsis if t.current_tst_level == 1]

    report = []
    for tsi in l1_tsis:
        tst = tst_repository.get_by_id(tsi.tst_id)
        if not tst:
            continue

        sla_days = tst.sla_days or 0
        is_completed = tsi.status.value == "COMPLETED"

        # Simple SLA check: if completed, assume on time (no actual_completion_date tracking)
        on_time = 1 if is_completed else 0
        late = 0  # Simplified: no overdue detection yet

        # Find existing entry or create
        existing = None
        for r in report:
            if r["tst_id"] == tst.tst_id:
                existing = r
                break

        if existing:
            existing["on_time"] += on_time
            existing["total"] += 1
        else:
            report.append({
                "tst_id": tst.tst_id,
                "tst_code": tst.tst_code,
                "tst_name": tst.tst_name,
                "sla_days": sla_days,
                "on_time": on_time,
                "late": late,
                "total": 1,
            })

    # Calculate compliance rate
    for r in report:
        total = r["total"]
        r["sla_compliance_rate"] = round(r["on_time"] / total * 100, 1) if total > 0 else 0.0

    return report


def get_workload_report():
    """Get workload report -- task count per employee.

    Returns list of {emp_id, emp_code, emp_name, task_count, completed_count, pending_count}.
    """
    all_tris = tri_repository.get_all()
    all_emps = emp_repository.get_all()

    # Build emp lookup
    emp_map = {e.emp_id: e for e in all_emps}

    # Count tasks per employee
    workload = {}
    for tri in all_tris:
        if tri.tsi_id is None:
            continue  # Base pool entry, not actual assignment
        emp_id = tri.emp_id
        if emp_id not in workload:
            emp = emp_map.get(emp_id)
            workload[emp_id] = {
                "emp_id": emp_id,
                "emp_code": emp.emp_code if emp else emp_id,
                "emp_name": emp.emp_name if emp else "Unknown",
                "task_count": 0,
                "completed_count": 0,
                "pending_count": 0,
            }

        workload[emp_id]["task_count"] += 1

        # Check status
        tsi = tsi_repository.get_by_id(tri.tsi_id)
        if tsi:
            if tsi.status.value == "COMPLETED":
                workload[emp_id]["completed_count"] += 1
            elif tsi.status.value in ("PENDING", "IN_PROGRESS"):
                workload[emp_id]["pending_count"] += 1

    return list(workload.values())
