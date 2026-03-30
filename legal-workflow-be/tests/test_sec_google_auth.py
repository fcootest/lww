"""Tests for Google OAuth + legacy login -- Step 5."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGoogleAuth:

    @patch("src.modules.sec.router.verify_google_token", return_value="trangph@apero.vn")
    def test_google_login_valid_token(self, mock_verify):
        resp = client.post("/api/auth/login", json={"google_token": "valid-token"})
        assert resp.status_code == 200
        assert resp.json()["data"]["user"]["empsec"] == "SEC1"

    @patch("src.modules.sec.router.verify_google_token", return_value=None)
    def test_google_login_invalid_token(self, mock_verify):
        resp = client.post("/api/auth/login", json={"google_token": "bad-token"})
        assert resp.status_code == 401

    @patch("src.modules.sec.router.verify_google_token", return_value="nobody@apero.vn")
    def test_google_login_email_not_in_system(self, mock_verify):
        resp = client.post("/api/auth/login", json={"google_token": "valid-but-unknown"})
        assert resp.status_code == 401

    def test_legacy_email_login_still_works(self):
        resp = client.post("/api/auth/login", json={"email": "trangph@apero.vn"})
        assert resp.status_code == 200

    def test_no_email_no_token_returns_400(self):
        resp = client.post("/api/auth/login", json={})
        assert resp.status_code == 400
