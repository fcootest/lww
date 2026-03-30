"""Dashboard service -- aggregate task statistics."""

from src.modules.tsi.repository import tsi_repository
from src.modules.tri.repository import tri_repository
from src.modules.tst.repository import tst_repository
from src.modules.emp.repository import emp_repository


def get_dashboard_data(emp_code=None, role=None):
    """Get dashboard summary data.

    Admin sees all tasks; others see only their own.
    """
    all_tsis = tsi_repository.get_all()

    # Role-scoped filtering
    if role != "ADMIN":
        emp = emp_repository.get_by_code(emp_code) if emp_code else None
        if emp:
            # Get TSI IDs assigned to this employee
            tri_list = tri_repository.get_by_emp(emp.emp_id)
            assigned_tsi_ids = {t.tsi_id for t in tri_list if t.tsi_id}
            # Also include TSIs they created (L1)
            all_tsis = [t for t in all_tsis if t.tsi_id in assigned_tsi_ids or t.current_tst_level == 1]

    # Summary counts
    summary = {
        "pending": sum(1 for t in all_tsis if t.status.value in ("PENDING", "PENDING_REVIEW")),
        "in_progress": sum(1 for t in all_tsis if t.status.value == "IN_PROGRESS"),
        "completed": sum(1 for t in all_tsis if t.status.value == "COMPLETED"),
        "overdue": 0,  # TODO: implement overdue check with due_date
    }

    # By type: group by L1 TST
    by_type = {}
    for tsi in all_tsis:
        if tsi.current_tst_level == 1:
            tst = tst_repository.get_by_id(tsi.tst_id)
            if tst:
                type_name = tst.tst_name.lower()
                if "copyright" in type_name:
                    by_type["copyright"] = by_type.get("copyright", 0) + 1
                elif "trademark" in type_name:
                    by_type["trademark"] = by_type.get("trademark", 0) + 1
                elif "policy" in type_name:
                    by_type["policy"] = by_type.get("policy", 0) + 1
                elif "contract" in type_name:
                    by_type["contract"] = by_type.get("contract", 0) + 1
                else:
                    by_type["other"] = by_type.get("other", 0) + 1

    # Ensure all expected keys exist
    for key in ("copyright", "trademark", "policy", "contract"):
        if key not in by_type:
            by_type[key] = 0

    return {
        "summary": summary,
        "by_type": by_type,
    }
