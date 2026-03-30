"""TRT service — business logic layer."""

from uuid import uuid4
from src.modules.trt.model import TRT, TST_TRT
from src.modules.trt.repository import trt_repository, tst_trt_repository
from src.modules.trt.schema import TRTCreateRequest, TRTUpdateRequest, TSTTRTCreateRequest
from src.modules.tst.repository import tst_repository


class TRTService:
    """Service layer for TRT operations."""

    def __init__(self):
        self.repo = trt_repository
        self.junction_repo = tst_trt_repository

    def list_all(self):
        """Get all TRTs."""
        return self.repo.get_all()

    def create(self, req: TRTCreateRequest) -> TRT:
        """Create a new TRT."""
        trt_id = f"TRT-{uuid4().hex[:8]}"
        trt = TRT(
            trt_id=trt_id,
            trt_code=req.trt_code,
            trt_name=req.trt_name,
            description=req.description,
        )
        return self.repo.create(trt)

    def map_to_tst(self, req: TSTTRTCreateRequest) -> TST_TRT:
        """Map a TRT to a TST. Validates both exist and no duplicate."""
        tst = tst_repository.get_by_id(req.tst_id)
        if tst is None:
            raise ValueError(f"TST '{req.tst_id}' not found")

        trt = self.repo.get_by_id(req.trt_id)
        if trt is None:
            raise ValueError(f"TRT '{req.trt_id}' not found")

        if self.junction_repo.exists(req.tst_id, req.trt_id):
            raise ValueError(f"Mapping TST '{req.tst_id}' -> TRT '{req.trt_id}' already exists")

        mapping = TST_TRT(
            tst_id=req.tst_id,
            trt_id=req.trt_id,
            is_required=req.is_required,
        )
        return self.junction_repo.create(mapping)


trt_service = TRTService()
