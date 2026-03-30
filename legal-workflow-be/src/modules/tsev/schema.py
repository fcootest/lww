"""TSEV request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TSEVCreateRequest(BaseModel):
    """Schema for creating a task event."""
    event_type: str = Field(..., min_length=1)
    event_data: Optional[str] = None
    tdi_id: Optional[str] = None
