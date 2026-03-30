"""TRI (TaskRoleInstance) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TRI(BaseModel):
    """TaskRoleInstance entity — assigns an employee to a task with a role."""
    tri_id: str
    trt_id: str  # FK -> TRT
    tsi_id: Optional[str] = None  # FK -> TSI, None for base pool
    emp_id: str  # FK -> EMP
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
