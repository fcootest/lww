"""TST service — business logic layer."""

from uuid import uuid4
from src.modules.tst.model import TST
from src.modules.tst.repository import tst_repository
from src.modules.tst.schema import TSTCreateRequest, TSTUpdateRequest


class TSTService:
    """Service layer for TST operations."""

    def __init__(self, repo=None):
        self.repo = repo or tst_repository

    def list_tree(self, root_id=None):
        """Get TST tree."""
        return self.repo.get_tree(root_id)

    def get_detail(self, tst_id: str):
        """Get single TST by ID."""
        return self.repo.get_by_id(tst_id)

    def create(self, req: TSTCreateRequest) -> TST:
        """Create a new TST. Validates parent exists for L2/L3."""
        if req.tst_level in (2, 3):
            if not req.my_parent_task:
                raise ValueError("my_parent_task is required for level 2 and 3")
            parent = self.repo.get_by_id(req.my_parent_task)
            if parent is None:
                raise ValueError(f"Parent TST '{req.my_parent_task}' not found")

        tst_id = f"TST-{uuid4().hex[:8]}"
        tst = TST(
            tst_id=tst_id,
            tst_code=req.tst_code,
            tst_name=req.tst_name,
            tst_level=req.tst_level,
            my_parent_task=req.my_parent_task,
            description=req.description,
            sla_days=req.sla_days,
        )
        return self.repo.create(tst)

    def update(self, tst_id: str, req: TSTUpdateRequest):
        """Update existing TST fields."""
        updates = req.model_dump(exclude_none=True)
        if not updates:
            return self.repo.get_by_id(tst_id)
        return self.repo.update(tst_id, updates)

    def delete(self, tst_id: str) -> bool:
        """Soft delete a TST."""
        return self.repo.soft_delete(tst_id)


tst_service = TSTService()
