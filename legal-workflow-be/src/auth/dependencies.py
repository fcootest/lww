"""FastAPI dependencies for authentication and authorization."""

from typing import Callable
from fastapi import Request, HTTPException
from src.auth.jwt_utils import decode_jwt
import jwt as pyjwt


async def get_current_user(request: Request) -> dict:
    """Extract and verify JWT from Authorization header.

    Sets request.state.user with decoded payload.
    Raises HTTPException 401 if missing/invalid/expired.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header[7:]  # strip "Bearer "

    try:
        payload = decode_jwt(token)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    request.state.user = payload
    return payload


def require_roles(allowed_roles: list[str]) -> Callable:
    """Dependency factory: restrict endpoint to specific roles.

    Usage: Depends(require_roles(["ADMIN", "LEGAL_MANAGER"]))
    """
    async def _check_role(request: Request) -> dict:
        user = await get_current_user(request)
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.get('role')}' not in allowed roles: {allowed_roles}",
            )
        return user

    return _check_role
