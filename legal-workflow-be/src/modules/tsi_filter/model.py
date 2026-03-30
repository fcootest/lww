"""TSI_Filter model — links filters to task instances."""

from pydantic import BaseModel


class TSIFilter(BaseModel):
    """TSI_Filter entity — maps filter criteria to task instances."""
    id: int
    tsi_id: str
    filter_type: str
    filter_code: str
