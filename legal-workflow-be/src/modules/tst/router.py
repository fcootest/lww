"""TST Config CRUD router."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.tst.service import tst_service
from src.modules.tst.schema import TSTCreateRequest, TSTUpdateRequest

router = APIRouter(
    prefix="/api/legal/config/tst",
    tags=["TST Config"],
)


@router.get("/")
async def list_tst(user: dict = Depends(get_current_user)):
    """List TST as tree."""
    tree = tst_service.list_tree()
    return send_success(data=[node.model_dump(mode="json") for node in tree])


@router.get("/{tst_id}")
async def get_tst(tst_id: str, user: dict = Depends(get_current_user)):
    """Get TST detail by ID."""
    tst = tst_service.get_detail(tst_id)
    if tst is None:
        return send_error(message=f"TST '{tst_id}' not found", status_code=404)
    return send_success(data=tst.model_dump(mode="json"))


@router.post("/")
async def create_tst(req: TSTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create a new TST (admin only)."""
    try:
        tst = tst_service.create(req)
        return send_success(data=tst.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


@router.put("/{tst_id}")
async def update_tst(tst_id: str, req: TSTUpdateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Update TST (admin only)."""
    result = tst_service.update(tst_id, req)
    if result is None:
        return send_error(message=f"TST '{tst_id}' not found", status_code=404)
    return send_success(data=result.model_dump(mode="json"))


@router.delete("/{tst_id}")
async def delete_tst(tst_id: str, user: dict = Depends(require_roles(["ADMIN"]))):
    """Soft delete TST (admin only)."""
    deleted = tst_service.delete(tst_id)
    if not deleted:
        return send_error(message=f"TST '{tst_id}' not found", status_code=404)
    return send_success(message="Deleted")
