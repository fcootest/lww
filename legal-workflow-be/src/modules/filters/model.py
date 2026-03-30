"""Filter Config models - TST_Filter + TST_TDT."""

from pydantic import BaseModel, field_validator


VALID_FILTER_TYPES = [
    "TLT", "TUT", "TST_FILTER", "TMT", "KR", "CDT", "PT", "LE", "CTY",
]


class TSTFilter(BaseModel):
    """TST_Filter - maps filter types to TST task types."""
    tst_id: str
    filter_type: str
    filter_code: str

    @field_validator("filter_type")
    @classmethod
    def validate_filter_type(cls, v: str) -> str:
        if v not in VALID_FILTER_TYPES:
            raise ValueError(f"filter_type must be one of {VALID_FILTER_TYPES}")
        return v


class TSTTDT(BaseModel):
    """TST_TDT - maps document types to TST task types."""
    tst_id: str
    tdt_id: str
    is_required: bool = False
