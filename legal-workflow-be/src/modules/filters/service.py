"""Filter Config service - business logic layer."""

from src.modules.filters.model import TSTFilter, TSTTDT
from src.modules.filters.repository import tst_filter_repository, tst_tdt_repository
from src.modules.filters.schema import TSTFilterCreateRequest, TSTTDTCreateRequest
from src.modules.tst.repository import tst_repository
from src.modules.tdt.repository import tdt_repository


class FilterConfigService:
    """Service layer for filter config operations."""

    def __init__(self):
        self.filter_repo = tst_filter_repository
        self.tdt_repo = tst_tdt_repository

    def create_tst_filter(self, req: TSTFilterCreateRequest) -> TSTFilter:
        """Create a TST_Filter mapping."""
        # Validate TST exists
        tst = tst_repository.get_by_id(req.tst_id)
        if tst is None:
            raise ValueError(f"TST '{req.tst_id}' not found")

        # Check duplicate
        if self.filter_repo.exists(req.tst_id, req.filter_type, req.filter_code):
            raise ValueError("This filter mapping already exists")

        item = TSTFilter(
            tst_id=req.tst_id,
            filter_type=req.filter_type,
            filter_code=req.filter_code,
        )
        return self.filter_repo.create(item)

    def create_tst_tdt(self, req: TSTTDTCreateRequest) -> TSTTDT:
        """Create a TST_TDT mapping."""
        # Validate TST exists
        tst = tst_repository.get_by_id(req.tst_id)
        if tst is None:
            raise ValueError(f"TST '{req.tst_id}' not found")

        # Validate TDT exists
        tdt = tdt_repository.get_by_id(req.tdt_id)
        if tdt is None:
            raise ValueError(f"TDT '{req.tdt_id}' not found")

        # Check duplicate
        if self.tdt_repo.exists(req.tst_id, req.tdt_id):
            raise ValueError("This TST-TDT mapping already exists")

        item = TSTTDT(
            tst_id=req.tst_id,
            tdt_id=req.tdt_id,
            is_required=req.is_required,
        )
        return self.tdt_repo.create(item)

    def get_filters_for_tst(self, tst_id: str) -> list[TSTFilter]:
        """Get all filters for a TST."""
        return self.filter_repo.get_by_tst(tst_id)

    def get_doc_types_for_tst(self, tst_id: str) -> list[TSTTDT]:
        """Get all doc type mappings for a TST."""
        return self.tdt_repo.get_by_tst(tst_id)


filter_config_service = FilterConfigService()
