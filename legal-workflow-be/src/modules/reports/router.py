"""Reports router -- SLA and Workload report APIs."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.common.response import send_success
from src.modules.reports.service import get_sla_report, get_workload_report

router = APIRouter(
    prefix="/api/legal/reports",
    tags=["Reports"],
)


@router.get("/sla")
async def sla_report(user: dict = Depends(get_current_user)):
    """Get SLA compliance report by task type."""
    data = get_sla_report()
    return send_success(data=data)


@router.get("/workload")
async def workload_report(user: dict = Depends(get_current_user)):
    """Get workload report -- task count per employee."""
    data = get_workload_report()
    return send_success(data=data)
