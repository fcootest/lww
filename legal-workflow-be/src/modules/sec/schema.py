"""SEC request/response schemas."""

from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: Optional[str] = None
    google_token: Optional[str] = None
