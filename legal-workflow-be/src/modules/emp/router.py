"""EMP router — employee list and detail APIs."""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.auth.dependencies import get_current_user
from src.common.response import send_success, send_error
from src.modules.emp.repository import emp_repository

router = APIRouter(
    prefix="/api/legal/emp",
    tags=["EMP"],
)


@router.get("/")
async def list_emp(
    department: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """List employees, optionally filtered by department."""
    items = emp_repository.get_all(department=department)
    return send_success(data=[item.model_dump(mode="json") for item in items])


@router.get("/{emp_code}")
async def get_emp(emp_code: str, user: dict = Depends(get_current_user)):
    """Get employee detail by code."""
    emp = emp_repository.get_by_code(emp_code)
    if emp is None:
        return send_error(message=f"Employee '{emp_code}' not found", status_code=404)
    return send_success(data=emp.model_dump(mode="json"))
