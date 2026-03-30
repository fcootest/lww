"""Workflow assignment — auto-assign employees to tasks based on roles."""

from uuid import uuid4
from src.modules.tsi.model import TSI
from src.modules.tsi.repository import tsi_repository
from src.modules.trt.repository import tst_trt_repository
from src.modules.tri.model import TRI
from src.modules.tri.repository import tri_repository


def assign_handler(tsi: TSI):
    """Auto-assign an employee to a TSI based on TST_TRT role mappings.

    1. TSI -> TST (get the task type)
    2. TST -> TST_TRT (get required roles)
    3. For each role, find EMP in TRI base pool with matching TRT
    4. Create TRI assignment
    5. Update TSI.assigned_to
    """
    # Get role mappings for this TST
    role_mappings = tst_trt_repository.get_by_tst(tsi.tst_id)
    if not role_mappings:
        return  # No roles defined, stay PENDING

    for mapping in role_mappings:
        # Find base pool entry for this role
        pool_entries = tri_repository.get_base_pool_by_trt(mapping.trt_id)
        if not pool_entries:
            continue

        # Take first available employee
        emp_id = pool_entries[0].emp_id

        # Check not already assigned
        if tri_repository.exists(tsi.tsi_id, emp_id, mapping.trt_id):
            continue

        # Create TRI assignment
        tri = TRI(
            tri_id=f"TRI-{uuid4().hex[:8]}",
            trt_id=mapping.trt_id,
            tsi_id=tsi.tsi_id,
            emp_id=emp_id,
        )
        tri_repository.create(tri)

        # Update TSI.assigned_to
        tsi_repository.update(tsi.tsi_id, {"assigned_to": emp_id})
