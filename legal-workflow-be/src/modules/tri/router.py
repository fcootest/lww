"""TRI router — role assignment APIs."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error
from src.modules.tri.schema import TRICreateRequest
from src.modules.tri.service import assign_role

router = APIRouter(
    prefix="/api/legal/tri",
    tags=["TRI Assignment"],
)


@router.post("/")
async def create_assignment(req: TRICreateRequest, user: dict = Depends(get_current_user)):
    """Assign an employee to a task with a role."""
    try:
        tri = assign_role(req)
        return send_success(
            data=tri.model_dump(mode="json"),
            message="Assigned",
            status_code=201,
        )
    except ValueError as e:
        return send_error(message=str(e), status_code=400)
