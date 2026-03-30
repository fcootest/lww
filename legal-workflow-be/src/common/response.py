"""Standard API response utilities."""

from typing import Any
from fastapi.responses import JSONResponse


def send_success(data: Any = None, message: str = "OK", status_code: int = 200) -> JSONResponse:
    """Standard success response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "message": message,
        },
    )


def send_error(message: str = "Internal Server Error", status_code: int = 500, detail: Any = None) -> JSONResponse:
    """Standard error response."""
    content = {
        "success": False,
        "data": None,
        "message": message,
    }
    if detail is not None:
        content["detail"] = detail
    return JSONResponse(
        status_code=status_code,
        content=content,
    )
