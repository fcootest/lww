"""SEC data filters -- PT and CDT filtering for task lists."""

from typing import Optional
from src.modules.sec.models import SecPermission

# cdt_1 -> cdt_code mapping
CDT1_TO_CODE = {
    "HQ1": "SHQ1", "HQ2": "SHQ2", "SMI": "CSM", "TER": "COR",
    "VIS": "CVL", "AST": "CAH", "SAP": "ASA", "MGM": "CMN",
}

# cdt_code -> parent_cdt_code
CDT_PARENT = {
    "SHQ1": "GAG", "SHQ2": "GAG", "CSM": "GAG", "COR": "GAG",
    "CVL": "GAG", "CAH": "GAG", "ASA": "GAG", "CMN": "GAG",
    "SHQ1-DEV": "SHQ1", "SHQ1-QA": "SHQ1", "CMN-HR": "CMN",
}


def get_task_filter_value(task: dict, filter_type: str) -> Optional[str]:
    """Extract a filter value from a task dict (from tsi_filter)."""
    filters = task.get("filters", [])
    for f in filters:
        if f.get("filter_type") == filter_type:
            return f.get("filter_code")
    return None


def pt_filter(tasks: list[dict], sec: SecPermission, allowed_pts: list[str] = None) -> list[dict]:
    """Filter tasks by PT allowed.

    - AllPT (SEC2/3/4): return all tasks
    - MyPT (SEC1): only tasks where PT is in allowed_pts list
    """
    if sec.pt_allowed == "AllPT":
        return tasks

    if not allowed_pts:
        allowed_pts = []

    result = []
    for task in tasks:
        task_pt = get_task_filter_value(task, "PT")
        if task_pt is None or task_pt in allowed_pts:
            result.append(task)
    return result


def cdt_filter(tasks: list[dict], sec: SecPermission, allowed_cdts: list[str] = None) -> list[dict]:
    """Filter tasks by CDT allowed.

    - AllCDT (SEC4): return all tasks
    - MyCDTParent (SEC2): tasks in own CDT or parent CDT
    - MyCDT (SEC1/SEC3): tasks in own CDT only
    """
    if sec.cdt_allowed == "AllCDT":
        return tasks

    if allowed_cdts is None:
        allowed_cdts = _derive_allowed_cdts(sec)

    result = []
    for task in tasks:
        task_cdt = get_task_filter_value(task, "CDT")
        if task_cdt is None or task_cdt in allowed_cdts:
            result.append(task)
    return result


def _derive_allowed_cdts(sec: SecPermission) -> list[str]:
    """Derive allowed CDT codes from SecPermission."""
    my_cdt = CDT1_TO_CODE.get(sec.cdt_1)
    if not my_cdt:
        return []

    if sec.cdt_allowed == "MyCDT":
        return [my_cdt]
    elif sec.cdt_allowed == "MyCDTParent":
        parent = CDT_PARENT.get(my_cdt)
        cdts = [my_cdt]
        if parent:
            cdts.append(parent)
        return cdts
    return []


def sec_filter(tasks: list[dict], sec: SecPermission, allowed_pts: list[str] = None, allowed_cdts: list[str] = None) -> list[dict]:
    """Apply both PT and CDT filters."""
    tasks = pt_filter(tasks, sec, allowed_pts)
    tasks = cdt_filter(tasks, sec, allowed_cdts)
    return tasks
