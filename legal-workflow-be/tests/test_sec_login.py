"""Tests for SEC login endpoint + middleware -- Steps 2 & 3."""

import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.auth.jwt_utils import decode_jwt


client = TestClient(app)


class TestSecLoginEndpoint:

    def test_login_valid_email(self):
        resp = client.post("/api/auth/login", json={"email": "trangph@apero.vn"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "token" in data
        assert data["user"]["empsec"] == "SEC1"

    def test_login_unknown_email(self):
        resp = client.post("/api/auth/login", json={"email": "xxx@apero.vn"})
        assert resp.status_code == 401

    def test_login_jwt_contains_sec_fields(self):
        resp = client.post("/api/auth/login", json={"email": "hoangdnh@apero.vn"})
        token = resp.json()["data"]["token"]
        payload = decode_jwt(token)
        assert payload["empsec"] == "SEC4"
        assert payload["pt_allowed"] == "AllPT"
        assert payload["cdt_allowed"] == "AllCDT"
        assert payload["krf_level"] == 7

    def test_login_missing_email(self):
        resp = client.post("/api/auth/login", json={})
        assert resp.status_code == 400  # no email or token provided

    def test_login_jwt_is_valid(self):
        resp = client.post("/api/auth/login", json={"email": "trangph@apero.vn"})
        token = resp.json()["data"]["token"]
        payload = decode_jwt(token)
        assert payload["emp_code"] == "F.00011"


class TestSecMiddleware:

    def _get_token(self, email: str) -> str:
        resp = client.post("/api/auth/login", json={"email": email})
        return resp.json()["data"]["token"]

    def test_protected_route_with_sec_token(self):
        token = self._get_token("trangph@apero.vn")
        resp = client.get("/api/test/protected", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        user = resp.json()["data"]
        assert user["empsec"] == "SEC1"

    def test_sec_fields_in_request_user(self):
        token = self._get_token("hoangdnh@apero.vn")
        resp = client.get("/api/test/protected", headers={"Authorization": f"Bearer {token}"})
        user = resp.json()["data"]
        assert user["pt_allowed"] == "AllPT"
        assert user["cdt_allowed"] == "AllCDT"
        assert user["krf_level"] == 7

    def test_unauthenticated_no_sec(self):
        resp = client.get("/api/test/protected")
        assert resp.status_code == 401
