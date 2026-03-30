"""Shared test helpers."""

import jwt
from src.config.settings import settings


def make_token(emp_code: str = "TiepTA", role: str = "LEGAL_MANAGER", emp_name: str = "Tran Anh Tiep") -> str:
    """Generate a valid JWT token for testing."""
    import time
    payload = {
        "emp_code": emp_code,
        "role": role,
        "emp_name": emp_name,
        "exp": int(time.time()) + 3600,  # 1 hour from now
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def make_expired_token(emp_code: str = "TiepTA", role: str = "LEGAL_MANAGER") -> str:
    """Generate an expired JWT token for testing."""
    payload = {
        "emp_code": emp_code,
        "role": role,
        "exp": 1000000000,  # far in the past
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def auth_header(token: str) -> dict:
    """Build Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}
