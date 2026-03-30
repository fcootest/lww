"""TDT (TaskDocumentType) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TDT(BaseModel):
    """TaskDocumentType entity — defines document types required for tasks."""
    tdt_id: str
    tdt_code: str
    tdt_name: str
    description: Optional[str] = None
    file_extensions: Optional[str] = None
    max_file_size_mb: Optional[int] = None
    is_required: Optional[bool] = False
    tdtp_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
