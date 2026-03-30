"""SEC permission data models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SecLevel(str, Enum):
    """EMPSEC security levels."""
    SEC1 = "SEC1"
    SEC2 = "SEC2"
    SEC3 = "SEC3"
    SEC4 = "SEC4"


class SecPermission(BaseModel):
    """SEC permission object for an employee.

    Maps to BigQuery view: fp-a-project.sec_data.v_auth_lookup
    """
    emp_code: str
    emp_name: str
    google_email: str
    empgrade: Optional[str] = None
    empsec: SecLevel = SecLevel.SEC1
    pt_allowed: str = "MyPT"
    cdt_allowed: str = "MyCDT"
    krf_level: int = 3
    cdt_1: Optional[str] = None
    cdt: Optional[str] = None
    role_legal: Optional[str] = "User"
