"""TST request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TSTCreateRequest(BaseModel):
    """Schema for creating a new TST."""
    tst_code: str = Field(..., min_length=1)
    tst_name: str = Field(..., min_length=1)
    tst_level: int = Field(..., ge=1, le=3)
    my_parent_task: Optional[str] = None
    description: Optional[str] = None
    sla_days: Optional[int] = None


class TSTUpdateRequest(BaseModel):
    """Schema for updating an existing TST."""
    tst_name: Optional[str] = None
    description: Optional[str] = None
    sla_days: Optional[int] = None
