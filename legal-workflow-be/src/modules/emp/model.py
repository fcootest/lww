"""EMP (Employee) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EMP(BaseModel):
    """Employee entity."""
    emp_id: str
    emp_code: str
    emp_name: str
    email: str
    department: Optional[str] = None
    position: Optional[str] = None
    grade_code: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
