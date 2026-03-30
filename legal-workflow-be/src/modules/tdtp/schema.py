"""TDTP request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Any


class TDTPCreateRequest(BaseModel):
    """Schema for creating a new TDTP."""
    tdt_id: str = Field(..., min_length=1)
    tdtp_code: str = Field(..., min_length=1)
    tdtp_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    template_file_ref: Optional[str] = None
    template_structure: Optional[Any] = None
    sample_data: Optional[Any] = None
    version: int = 1


class TDTPUpdateRequest(BaseModel):
    """Schema for updating an existing TDTP."""
    tdtp_name: Optional[str] = None
    description: Optional[str] = None
    template_file_ref: Optional[str] = None
    template_structure: Optional[Any] = None
    sample_data: Optional[Any] = None
    version: Optional[int] = None
