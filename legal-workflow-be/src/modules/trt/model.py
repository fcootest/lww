"""TRT (TaskRoleType) entity model + TST_TRT junction."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TRT(BaseModel):
    """TaskRoleType entity — defines roles for tasks."""
    trt_id: str
    trt_code: str
    trt_name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TST_TRT(BaseModel):
    """Junction table: maps TRT roles to TST task types."""
    tst_id: str
    trt_id: str
    is_required: bool = False
