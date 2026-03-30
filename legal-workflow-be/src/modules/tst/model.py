"""TST (TaskType) entity model."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TST(BaseModel):
    """TaskType entity — hierarchical 3-level structure."""
    tst_id: str
    tst_code: str
    tst_name: str
    tst_level: int = Field(ge=1, le=3)
    my_parent_task: Optional[str] = None
    description: Optional[str] = None
    sla_days: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("tst_level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("tst_level must be 1, 2, or 3")
        return v


class TSTTreeNode(BaseModel):
    """TST with nested children for tree representation."""
    tst_id: str
    tst_code: str
    tst_name: str
    tst_level: int
    my_parent_task: Optional[str] = None
    description: Optional[str] = None
    sla_days: Optional[int] = None
    is_active: bool = True
    children: list["TSTTreeNode"] = []
