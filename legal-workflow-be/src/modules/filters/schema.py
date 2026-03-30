"""Filter Config request/response schemas."""

from pydantic import BaseModel, Field, field_validator
from src.modules.filters.model import VALID_FILTER_TYPES


class TSTFilterCreateRequest(BaseModel):
    """Schema for creating a TST_Filter mapping."""
    tst_id: str = Field(..., min_length=1)
    filter_type: str = Field(..., min_length=1)
    filter_code: str = Field(..., min_length=1)

    @field_validator("filter_type")
    @classmethod
    def validate_filter_type(cls, v: str) -> str:
        if v not in VALID_FILTER_TYPES:
            raise ValueError(f"filter_type must be one of {VALID_FILTER_TYPES}")
        return v


class TSTTDTCreateRequest(BaseModel):
    """Schema for creating a TST_TDT mapping."""
    tst_id: str = Field(..., min_length=1)
    tdt_id: str = Field(..., min_length=1)
    is_required: bool = False
