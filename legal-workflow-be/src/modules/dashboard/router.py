"""Dashboard router -- summary statistics API."""

from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.common.response import send_success
from src.modules.dashboard.service import get_dashboard_data

router = APIRouter(
    prefix="/api/legal",
    tags=["Dashboard"],
)


@router.get("/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    """Get dashboard summary data."""
    emp_code = user.get("emp_code", "")
    role = user.get("role", "")
    data = get_dashboard_data(emp_code=emp_code, role=role)
    return send_success(data=data)
