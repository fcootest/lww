"""TDI (TaskDocumentInstance) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TDIStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class TDI(BaseModel):
    """TaskDocumentInstance entity — a document uploaded to a task."""
    tdi_id: str
    tdt_id: str  # FK -> TDT
    tsi_id: str  # FK -> TSI
    file_name: str
    file_url: str
    file_size_bytes: Optional[int] = None
    version: int = 1
    uploaded_by: str  # FK -> EMP
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: TDIStatus = TDIStatus.ACTIVE
    notes: Optional[str] = None
