"""Filter Config CRUD router - TST_Filter + TST_TDT."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.filters.service import filter_config_service
from src.modules.filters.schema import TSTFilterCreateRequest, TSTTDTCreateRequest

router = APIRouter(
    prefix="/api/legal/config",
    tags=["Filter Config"],
)


@router.post("/tst-filter")
async def create_tst_filter(req: TSTFilterCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create TST_Filter mapping (admin only)."""
    try:
        item = filter_config_service.create_tst_filter(req)
        return send_success(data=item.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


@router.post("/tst-tdt")
async def create_tst_tdt(req: TSTTDTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create TST_TDT mapping (admin only)."""
    try:
        item = filter_config_service.create_tst_tdt(req)
        return send_success(data=item.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)


@router.get("/tst/{tst_id}/full")
async def get_tst_full(tst_id: str, user: dict = Depends(get_current_user)):
    """Get TST with filters and doc_types included."""
    from src.modules.tst.repository import tst_repository
    tst = tst_repository.get_by_id(tst_id)
    if tst is None:
        return send_error(message=f"TST '{tst_id}' not found", status_code=404)

    filters = filter_config_service.get_filters_for_tst(tst_id)
    doc_types = filter_config_service.get_doc_types_for_tst(tst_id)

    result = tst.model_dump(mode="json")
    result["filters"] = [f.model_dump(mode="json") for f in filters]
    result["doc_types"] = [d.model_dump(mode="json") for d in doc_types]

    return send_success(data=result)
