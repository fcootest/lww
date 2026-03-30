"""TRI request/response schemas."""

from pydantic import BaseModel, Field


class TRICreateRequest(BaseModel):
    """Schema for assigning an employee to a task with a role."""
    trt_id: str = Field(..., min_length=1)
    tsi_id: str = Field(..., min_length=1)
    emp_id: str = Field(..., min_length=1)
