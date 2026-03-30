"""Google OAuth2 token verification."""

from typing import Optional


def verify_google_token(token: str) -> Optional[str]:
    """Verify Google ID token and return email. Returns None if invalid."""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        from src.config.settings import settings

        client_id = settings.GOOGLE_CLIENT_ID or None
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        return idinfo.get("email")
    except Exception as e:
        print(f"[Google Auth] Verification failed: {e}")
        return None
