"""TDTP Config CRUD router."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.tdtp.service import tdtp_service
from src.modules.tdtp.schema import TDTPCreateRequest, TDTPUpdateRequest

router = APIRouter(
    prefix="/api/legal/config/tdtp",
    tags=["TDTP Config"],
)


@router.get("/")
async def list_tdtp(user: dict = Depends(get_current_user)):
    """List TDTPs."""
    items = tdtp_service.list_all()
    return send_success(data=[item.model_dump(mode="json") for item in items])


@router.post("/")
async def create_tdtp(req: TDTPCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create a new TDTP linked to TDT (admin only). Enforces 1:1."""
    try:
        tdtp = tdtp_service.create(req)
        return send_success(data=tdtp.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


@router.put("/{tdtp_id}")
async def update_tdtp(tdtp_id: str, req: TDTPUpdateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Update TDTP (admin only)."""
    result = tdtp_service.update(tdtp_id, req)
    if result is None:
        return send_error(message=f"TDTP '{tdtp_id}' not found", status_code=404)
    return send_success(data=result.model_dump(mode="json"))


@router.delete("/{tdtp_id}")
async def delete_tdtp(tdtp_id: str, user: dict = Depends(require_roles(["ADMIN"]))):
    """Soft delete TDTP (admin only)."""
    deleted = tdtp_service.delete(tdtp_id)
    if not deleted:
        return send_error(message=f"TDTP '{tdtp_id}' not found", status_code=404)
    return send_success(message="Deleted")
