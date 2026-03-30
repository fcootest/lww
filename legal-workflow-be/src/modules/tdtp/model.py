"""TDTP (TaskDocumentTypeTemplate) entity model."""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class TDTP(BaseModel):
    """TaskDocumentTypeTemplate entity — template for document types (1:1 with TDT)."""
    tdtp_id: str
    tdt_id: str  # UNIQUE — one template per document type
    tdtp_code: str
    tdtp_name: str
    description: Optional[str] = None
    template_file_ref: Optional[str] = None
    template_structure: Optional[Any] = None  # JSON
    sample_data: Optional[Any] = None  # JSON
    version: int = 1
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
