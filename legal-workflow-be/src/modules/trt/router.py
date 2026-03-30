"""TRT Config CRUD router."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user, require_roles
from src.common.response import send_success, send_error
from src.modules.trt.service import trt_service
from src.modules.trt.schema import TRTCreateRequest, TSTTRTCreateRequest

router = APIRouter(
    prefix="/api/legal/config",
    tags=["TRT Config"],
)


@router.get("/trt")
async def list_trt(user: dict = Depends(get_current_user)):
    """List TRTs."""
    items = trt_service.list_all()
    return send_success(data=[item.model_dump(mode="json") for item in items])


@router.post("/trt")
async def create_trt(req: TRTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Create a new TRT (admin only)."""
    trt = trt_service.create(req)
    return send_success(data=trt.model_dump(mode="json"), message="Created", status_code=201)


@router.post("/tst-trt")
async def create_tst_trt(req: TSTTRTCreateRequest, user: dict = Depends(require_roles(["ADMIN"]))):
    """Map a TRT role to a TST task type (admin only)."""
    try:
        mapping = trt_service.map_to_tst(req)
        return send_success(data=mapping.model_dump(mode="json"), message="Created", status_code=201)
    except ValueError as e:
        return send_error(message=str(e), status_code=400)
