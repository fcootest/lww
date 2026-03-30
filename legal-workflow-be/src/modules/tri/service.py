"""TRI service — business logic for role assignment."""

from uuid import uuid4
from src.modules.tri.model import TRI
from src.modules.tri.repository import tri_repository
from src.modules.tri.schema import TRICreateRequest
from src.modules.trt.repository import trt_repository
from src.modules.emp.repository import emp_repository
from src.modules.tsi.repository import tsi_repository


def assign_role(req: TRICreateRequest) -> TRI:
    """Assign an employee to a task with a role.

    Validates: TRT exists, EMP exists, TSI exists, not already assigned.
    """
    # Validate TRT
    trt = trt_repository.get_by_id(req.trt_id)
    if trt is None:
        raise ValueError(f"TRT '{req.trt_id}' not found")

    # Validate EMP
    emp = emp_repository.get_by_id(req.emp_id)
    if emp is None:
        raise ValueError(f"Employee '{req.emp_id}' not found")

    # Validate TSI
    tsi = tsi_repository.get_by_id(req.tsi_id)
    if tsi is None:
        raise ValueError(f"TSI '{req.tsi_id}' not found")

    # Check not already assigned
    if tri_repository.exists(req.tsi_id, req.emp_id, req.trt_id):
        raise ValueError(f"Employee '{req.emp_id}' already assigned to task '{req.tsi_id}' with role '{req.trt_id}'")

    # Create TRI
    tri = TRI(
        tri_id=f"TRI-{uuid4().hex[:8]}",
        trt_id=req.trt_id,
        tsi_id=req.tsi_id,
        emp_id=req.emp_id,
    )
    tri_repository.create(tri)

    # Update TSI.assigned_to
    tsi_repository.update(req.tsi_id, {"assigned_to": req.emp_id})

    return tri
