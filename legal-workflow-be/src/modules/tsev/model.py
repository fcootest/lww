"""TSEV (TaskEvent) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TSEVEventType(str, Enum):
    CREATE = "CREATE"
    UPLOAD = "UPLOAD"
    VIEW = "VIEW"
    UPDATE = "UPDATE"
    COMMENT = "COMMENT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REASSIGN = "REASSIGN"


class TSEV(BaseModel):
    """TaskEvent entity — logs events on task instances."""
    tsev_id: str
    tsi_id: str
    event_type: TSEVEventType
    emp_id: str
    event_data: Optional[str] = None  # JSON string
    tdi_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
