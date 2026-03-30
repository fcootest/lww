"""TSI request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TSIFilterInput(BaseModel):
    """Single filter input for task creation."""
    filter_type: str = Field(..., min_length=1)
    filter_code: str = Field(..., min_length=1)


class TSICreateRequest(BaseModel):
    """Schema for creating a new task (TSI L1)."""
    tst_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    filters: list[TSIFilterInput] = []
