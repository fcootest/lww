"""TNT (TaskNextTask / Transition) entity model."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TNT(BaseModel):
    """TaskNextTask entity — defines transitions between task types."""
    tnt_id: str
    from_tst_id: str
    to_tst_id: str
    condition_expression: Optional[str] = None
    condition_description: Optional[str] = None
    priority: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
