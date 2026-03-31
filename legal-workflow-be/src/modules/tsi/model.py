"""TSI (TaskInstance) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TSIStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_REVIEW = "PENDING_REVIEW"
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TSIPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TSI(BaseModel):
    """TaskInstance entity — a concrete task instance."""
    tsi_id: str
    tsi_code: str
    tst_id: str  # FK -> TST
    my_parent_task: Optional[str] = None  # FK -> TSI
    title: str
    description: Optional[str] = None
    status: TSIStatus = TSIStatus.DRAFT
    priority: Optional[TSIPriority] = None
    requested_by: Optional[str] = None  # FK -> EMP
    assigned_to: Optional[str] = None  # FK -> EMP
    due_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    current_tst_level: Optional[int] = None
    current_tst_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[str] = None  # JSON string for additional fields
    updated_at: datetime = Field(default_factory=datetime.utcnow)
