"""TNT service — business logic layer."""

from uuid import uuid4
from typing import Optional
from src.modules.tnt.model import TNT
from src.modules.tnt.repository import tnt_repository
from src.modules.tnt.schema import TNTCreateRequest, TNTUpdateRequest
from src.modules.tst.repository import tst_repository


class TNTService:
    """Service layer for TNT operations."""

    def __init__(self, repo=None):
        self.repo = repo or tnt_repository

    def list_all(self, from_tst_id: Optional[str] = None):
        """Get all TNTs, optionally filtered."""
        return self.repo.get_all(from_tst_id)

    def get_detail(self, tnt_id: str):
        """Get single TNT by ID."""
        return self.repo.get_by_id(tnt_id)

    def create(self, req: TNTCreateRequest) -> TNT:
        """Create a new TNT. Validates from/to TST exist."""
        from_tst = tst_repository.get_by_id(req.from_tst_id)
        if from_tst is None:
            raise ValueError(f"from_tst_id '{req.from_tst_id}' not found")
        to_tst = tst_repository.get_by_id(req.to_tst_id)
        if to_tst is None:
            raise ValueError(f"to_tst_id '{req.to_tst_id}' not found")

        tnt_id = f"TNT-{uuid4().hex[:8]}"
        tnt = TNT(
            tnt_id=tnt_id,
            from_tst_id=req.from_tst_id,
            to_tst_id=req.to_tst_id,
            condition_expression=req.condition_expression,
            condition_description=req.condition_description,
            priority=req.priority,
        )
        return self.repo.create(tnt)

    def update(self, tnt_id: str, req: TNTUpdateRequest):
        """Update existing TNT fields."""
        updates = req.model_dump(exclude_none=True)
        if not updates:
            return self.repo.get_by_id(tnt_id)
        return self.repo.update(tnt_id, updates)

    def delete(self, tnt_id: str) -> bool:
        """Soft delete a TNT."""
        return self.repo.delete(tnt_id)


tnt_service = TNTService()
