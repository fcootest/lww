"""TSEV router — task event APIs."""

from uuid import uuid4
from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error
from src.modules.tsev.model import TSEV, TSEVEventType
from src.modules.tsev.repository import tsev_repository
from src.modules.tsev.schema import TSEVCreateRequest
from src.modules.tsi.repository import tsi_repository

router = APIRouter(
    prefix="/api/legal/task",
    tags=["TSEV Events"],
)

VALID_MANUAL_EVENTS = {"COMMENT", "VIEW", "UPDATE"}


@router.post("/{tsi_id}/event")
async def create_event(tsi_id: str, req: TSEVCreateRequest, user: dict = Depends(get_current_user)):
    """Create a task event (COMMENT, VIEW, UPDATE)."""
    # Validate TSI exists
    tsi = tsi_repository.get_by_id(tsi_id)
    if tsi is None:
        return send_error(message=f"TSI '{tsi_id}' not found", status_code=404)

    # Validate event type
    try:
        event_type = TSEVEventType(req.event_type)
    except ValueError:
        return send_error(
            message=f"Invalid event_type '{req.event_type}'. Must be one of: {[e.value for e in TSEVEventType]}",
            status_code=422,
        )

    if event_type.value not in VALID_MANUAL_EVENTS:
        return send_error(
            message=f"Event type '{req.event_type}' cannot be created manually. Use COMMENT, VIEW, or UPDATE.",
            status_code=422,
        )

    tsev = TSEV(
        tsev_id=f"TSEV-{uuid4().hex[:8]}",
        tsi_id=tsi_id,
        event_type=event_type,
        emp_id=user.get("emp_code", "SYSTEM"),
        event_data=req.event_data,
        tdi_id=req.tdi_id,
    )
    tsev_repository.create(tsev)

    return send_success(
        data=tsev.model_dump(mode="json"),
        message="Event created",
        status_code=201,
    )
