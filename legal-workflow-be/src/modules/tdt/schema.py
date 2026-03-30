"""TDT request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TDTCreateRequest(BaseModel):
    """Schema for creating a new TDT."""
    tdt_code: str = Field(..., min_length=1)
    tdt_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    file_extensions: Optional[str] = None
    max_file_size_mb: Optional[int] = None
    is_required: Optional[bool] = False


class TDTUpdateRequest(BaseModel):
    """Schema for updating an existing TDT."""
    tdt_name: Optional[str] = None
    description: Optional[str] = None
    file_extensions: Optional[str] = None
    max_file_size_mb: Optional[int] = None
    is_required: Optional[bool] = None
