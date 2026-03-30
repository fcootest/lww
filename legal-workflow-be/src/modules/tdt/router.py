"""TDT Config CRUD router."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.tdt.service import tdt_service
from src.modules.tdt.schema import TDTCreateRequest, TDTUpdateRequest

router = APIRouter(
    prefix="/api/legal/config/tdt",
    tags=["TDT Config"],
)


@router.get("/")
async def list_tdt(user: dict = Depends(get_current_user)):
    """List TDTs with nested TDTP."""
    items = tdt_service.list_all()
    return send_success(data=items)


@router.get("/{tdt_id}")
async def get_tdt(tdt_id: str, user: dict = Depends(get_current_user)):
    """Get TDT detail by ID."""
    tdt = tdt_service.get_detail(tdt_id)
    if tdt is None:
        return send_error(message=f"TDT '{tdt_id}' not found", status_code=404)
    return send_success(data=tdt.model_dump(mode="json"))


@router.post("/")
async def create_tdt(req: TDTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create a new TDT (admin only)."""
    tdt = tdt_service.create(req)
    return send_success(data=tdt.model_dump(mode="json"), message="Created", status_code=201)


@router.put("/{tdt_id}")
async def update_tdt(tdt_id: str, req: TDTUpdateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Update TDT (admin only)."""
    result = tdt_service.update(tdt_id, req)
    if result is None:
        return send_error(message=f"TDT '{tdt_id}' not found", status_code=404)
    return send_success(data=result.model_dump(mode="json"))


@router.delete("/{tdt_id}")
async def delete_tdt(tdt_id: str, user: dict = Depends(require_roles(["ADMIN"]))):
    """Soft delete TDT (admin only)."""
    deleted = tdt_service.delete(tdt_id)
    if not deleted:
        return send_error(message=f"TDT '{tdt_id}' not found", status_code=404)
    return send_success(message="Deleted")
