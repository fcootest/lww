"""TDI request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TDICreateRequest(BaseModel):
    """Schema for uploading a document to a task."""
    tdt_id: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    file_url: str = Field(..., min_length=1)
    notes: Optional[str] = None
