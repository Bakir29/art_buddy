"""
Tests for app/auth/security.py

Covers:
- Password hashing and verification
- JWT token creation and decoding
- Token expiry and invalid tokens
"""

import pytest
from datetime import timedelta
from unittest.mock import patch

from app.auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


# ─── Password hashing ─────────────────────────────────────────────────────────

class TestPasswordHashing:

    def test_hash_returns_string(self):
        hashed = get_password_hash("mysecretpassword")
        assert isinstance(hashed, str)

    def test_hash_is_not_plain_text(self):
        plain = "mysecretpassword"
        hashed = get_password_hash(plain)
        assert hashed != plain

    def test_two_hashes_of_same_password_differ(self):
        """PBKDF2-sha256 uses a random salt per hash."""
        h1 = get_password_hash("password123")
        h2 = get_password_hash("password123")
        assert h1 != h2

    def test_verify_correct_password_returns_true(self):
        hashed = get_password_hash("correct_horse")
        assert verify_password("correct_horse", hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = get_password_hash("correct_horse")
        assert verify_password("wrong_horse", hashed) is False

    def test_verify_empty_password_returns_false(self):
        hashed = get_password_hash("correct_horse")
        assert verify_password("", hashed) is False

    def test_hash_round_trip_with_special_chars(self):
        plain = "P@$$w0rd!#%&*()"
        hashed = get_password_hash(plain)
        assert verify_password(plain, hashed) is True


# ─── JWT tokens ───────────────────────────────────────────────────────────────

class TestJWTTokens:

    def test_create_token_returns_string(self):
        token = create_access_token({"sub": "user@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_returns_email(self):
        email = "artist@artbuddy.com"
        token = create_access_token({"sub": email})
        result = decode_access_token(token)
        assert result == email

    def test_custom_expiry_is_respected(self):
        """Token with long expiry should decode cleanly."""
        token = create_access_token({"sub": "user@test.com"}, expires_delta=timedelta(hours=1))
        assert decode_access_token(token) == "user@test.com"

    def test_expired_token_raises_401(self):
        from fastapi import HTTPException
        token = create_access_token({"sub": "user@test.com"}, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises_401(self):
        from fastapi import HTTPException
        token = create_access_token({"sub": "user@test.com"})
        bad_token = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(bad_token)
        assert exc_info.value.status_code == 401

    def test_token_missing_sub_raises_401(self):
        """A token without a 'sub' claim should be rejected."""
        from fastapi import HTTPException
        token = create_access_token({"data": "no_subject_here"})
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_completely_invalid_string_raises_401(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not.a.token")
        assert exc_info.value.status_code == 401
