"""TNT Config CRUD router."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.tnt.service import tnt_service
from src.modules.tnt.schema import TNTCreateRequest, TNTUpdateRequest

router = APIRouter(
    prefix="/api/legal/config/tnt",
    tags=["TNT Config"],
)


@router.get("/")
async def list_tnt(
    from_tst_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """List TNTs, optionally filtered by from_tst_id."""
    items = tnt_service.list_all(from_tst_id)
    return send_success(data=[item.model_dump(mode="json") for item in items])


@router.post("/")
async def create_tnt(req: TNTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create a new TNT (admin only)."""
    try:
        tnt = tnt_service.create(req)
        return send_success(data=tnt.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


@router.put("/{tnt_id}")
async def update_tnt(tnt_id: str, req: TNTUpdateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Update TNT (admin only)."""
    result = tnt_service.update(tnt_id, req)
    if result is None:
        return send_error(message=f"TNT '{tnt_id}' not found", status_code=404)
    return send_success(data=result.model_dump(mode="json"))


@router.delete("/{tnt_id}")
async def delete_tnt(tnt_id: str, user: dict = Depends(require_roles(["ADMIN"]))):
    """Soft delete TNT (admin only)."""
    deleted = tnt_service.delete(tnt_id)
    if not deleted:
        return send_error(message=f"TNT '{tnt_id}' not found", status_code=404)
    return send_success(message="Deleted")
