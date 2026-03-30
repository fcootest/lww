"""Step 1: Auth & Roles middleware tests."""

import pytest
from tests.helpers import make_token, make_expired_token, auth_header


class TestAuthMiddleware:
    """Test JWT authentication dependency."""

    @pytest.mark.asyncio
    async def test_no_auth_header_returns_401(self, client):
        """Request without Authorization header returns 401."""
        response = await client.get("/api/test/protected")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client):
        """Request with garbage token returns 401."""
        response = await client.get(
            "/api/test/protected",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, client):
        """Request with expired JWT returns 401."""
        token = make_expired_token()
        response = await client.get(
            "/api/test/protected",
            headers=auth_header(token),
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_passes(self, client):
        """Request with valid JWT passes authentication."""
        token = make_token(emp_code="TiepTA", role="LEGAL_MANAGER")
        response = await client.get(
            "/api/test/protected",
            headers=auth_header(token),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_valid_token_returns_user_info(self, client):
        """Authenticated request returns user info from JWT payload."""
        token = make_token(emp_code="TiepTA", role="LEGAL_MANAGER", emp_name="Tran Anh Tiep")
        response = await client.get(
            "/api/test/protected",
            headers=auth_header(token),
        )
        data = response.json()
        assert data["data"]["emp_code"] == "TiepTA"
        assert data["data"]["role"] == "LEGAL_MANAGER"
        assert data["data"]["emp_name"] == "Tran Anh Tiep"

    @pytest.mark.asyncio
    async def test_bearer_prefix_required(self, client):
        """Token without 'Bearer ' prefix returns 401."""
        token = make_token()
        response = await client.get(
            "/api/test/protected",
            headers={"Authorization": token},  # missing "Bearer "
        )
        assert response.status_code == 401


class TestRolesMiddleware:
    """Test role-based authorization dependency."""

    @pytest.mark.asyncio
    async def test_allowed_role_passes(self, client):
        """User with allowed role can access endpoint."""
        token = make_token(role="ADMIN")
        response = await client.get(
            "/api/test/admin-only",
            headers=auth_header(token),
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_disallowed_role_returns_403(self, client):
        """User with disallowed role gets 403."""
        token = make_token(role="LEGAL_INTERN")
        response = await client.get(
            "/api/test/admin-only",
            headers=auth_header(token),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_multiple_allowed_roles(self, client):
        """Endpoint allowing multiple roles works for each."""
        for role in ["ADMIN", "LEGAL_MANAGER"]:
            token = make_token(role=role)
            response = await client.get(
                "/api/test/manager-or-admin",
                headers=auth_header(token),
            )
            assert response.status_code == 200, f"Role {role} should be allowed"

    @pytest.mark.asyncio
    async def test_forbidden_role_on_multi_role_endpoint(self, client):
        """Role not in allowed list gets 403 even on multi-role endpoint."""
        token = make_token(role="LEGAL_INTERN")
        response = await client.get(
            "/api/test/manager-or-admin",
            headers=auth_header(token),
        )
        assert response.status_code == 403


class TestMakeTokenHelper:
    """Test the make_token test helper itself."""

    def test_make_token_generates_valid_jwt(self):
        """make_token produces a decodable JWT."""
        import jwt as pyjwt
        from src.config.settings import settings
        token = make_token("MinhPT", "PRODUCT_MANAGER")
        payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["emp_code"] == "MinhPT"
        assert payload["role"] == "PRODUCT_MANAGER"

    def test_make_token_has_expiration(self):
        """make_token includes exp claim."""
        import jwt as pyjwt
        from src.config.settings import settings
        token = make_token()
        payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload
