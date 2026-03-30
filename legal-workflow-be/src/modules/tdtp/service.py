"""TDTP service — business logic layer."""

from uuid import uuid4
from src.modules.tdtp.model import TDTP
from src.modules.tdtp.repository import tdtp_repository
from src.modules.tdtp.schema import TDTPCreateRequest, TDTPUpdateRequest
from src.modules.tdt.repository import tdt_repository


class TDTPService:
    """Service layer for TDTP operations."""

    def __init__(self, repo=None):
        self.repo = repo or tdtp_repository

    def list_all(self):
        """Get all TDTPs."""
        return self.repo.get_all()

    def get_detail(self, tdtp_id: str):
        """Get single TDTP by ID."""
        return self.repo.get_by_id(tdtp_id)

    def create(self, req: TDTPCreateRequest) -> TDTP:
        """Create a new TDTP linked to TDT. Enforces 1:1."""
        # Validate TDT exists
        tdt = tdt_repository.get_by_id(req.tdt_id)
        if tdt is None:
            raise ValueError(f"TDT '{req.tdt_id}' not found")

        # Enforce 1:1 — check if TDT already has a template
        existing = self.repo.get_by_tdt_id(req.tdt_id)
        if existing is not None:
            raise ValueError(f"TDT '{req.tdt_id}' already has a template (TDTP '{existing.tdtp_id}')")

        tdtp_id = f"TDTP-{uuid4().hex[:8]}"
        tdtp = TDTP(
            tdtp_id=tdtp_id,
            tdt_id=req.tdt_id,
            tdtp_code=req.tdtp_code,
            tdtp_name=req.tdtp_name,
            description=req.description,
            template_file_ref=req.template_file_ref,
            template_structure=req.template_structure,
            sample_data=req.sample_data,
            version=req.version,
        )
        result = self.repo.create(tdtp)

        # Link back to TDT
        tdt_repository.update(req.tdt_id, {"tdtp_id": tdtp_id})

        return result

    def update(self, tdtp_id: str, req: TDTPUpdateRequest):
        """Update existing TDTP."""
        updates = req.model_dump(exclude_none=True)
        if not updates:
            return self.repo.get_by_id(tdtp_id)
        return self.repo.update(tdtp_id, updates)

    def delete(self, tdtp_id: str) -> bool:
        """Soft delete a TDTP."""
        return self.repo.delete(tdtp_id)


tdtp_service = TDTPService()
