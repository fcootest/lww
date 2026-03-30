"""TRT request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TRTCreateRequest(BaseModel):
    """Schema for creating a new TRT."""
    trt_code: str = Field(..., min_length=1)
    trt_name: str = Field(..., min_length=1)
    description: Optional[str] = None


class TRTUpdateRequest(BaseModel):
    """Schema for updating an existing TRT."""
    trt_name: Optional[str] = None
    description: Optional[str] = None


class TSTTRTCreateRequest(BaseModel):
    """Schema for mapping a TRT to a TST."""
    tst_id: str = Field(..., min_length=1)
    trt_id: str = Field(..., min_length=1)
    is_required: bool = False
