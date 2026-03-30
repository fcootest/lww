"""TNT request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TNTCreateRequest(BaseModel):
    """Schema for creating a new TNT."""
    from_tst_id: str = Field(..., min_length=1)
    to_tst_id: str = Field(..., min_length=1)
    condition_expression: Optional[str] = None
    condition_description: Optional[str] = None
    priority: Optional[int] = None


class TNTUpdateRequest(BaseModel):
    """Schema for updating an existing TNT."""
    condition_expression: Optional[str] = None
    condition_description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
