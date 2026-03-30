"""TDT service — business logic layer."""

from uuid import uuid4
from src.modules.tdt.model import TDT
from src.modules.tdt.repository import tdt_repository
from src.modules.tdt.schema import TDTCreateRequest, TDTUpdateRequest


class TDTService:
    """Service layer for TDT operations."""

    def __init__(self, repo=None):
        self.repo = repo or tdt_repository

    def list_all(self):
        """Get all TDTs with nested TDTP data."""
        from src.modules.tdtp.repository import tdtp_repository
        items = self.repo.get_all()
        result = []
        for item in items:
            item_dict = item.model_dump(mode="json")
            # Include nested TDTP if linked
            if item.tdtp_id:
                tdtp = tdtp_repository.get_by_id(item.tdtp_id)
                item_dict["tdtp"] = tdtp.model_dump(mode="json") if tdtp else None
            else:
                item_dict["tdtp"] = None
            result.append(item_dict)
        return result

    def get_detail(self, tdt_id: str):
        """Get single TDT by ID."""
        return self.repo.get_by_id(tdt_id)

    def create(self, req: TDTCreateRequest) -> TDT:
        """Create a new TDT."""
        tdt_id = f"TDT-{uuid4().hex[:8]}"
        tdt = TDT(
            tdt_id=tdt_id,
            tdt_code=req.tdt_code,
            tdt_name=req.tdt_name,
            description=req.description,
            file_extensions=req.file_extensions,
            max_file_size_mb=req.max_file_size_mb,
            is_required=req.is_required,
        )
        return self.repo.create(tdt)

    def update(self, tdt_id: str, req: TDTUpdateRequest):
        """Update existing TDT."""
        updates = req.model_dump(exclude_none=True)
        if not updates:
            return self.repo.get_by_id(tdt_id)
        return self.repo.update(tdt_id, updates)

    def delete(self, tdt_id: str) -> bool:
        """Soft delete a TDT."""
        return self.repo.delete(tdt_id)


tdt_service = TDTService()
