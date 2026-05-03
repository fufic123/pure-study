import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.services.token_service import TokenService


@pytest.fixture
def svc() -> TokenService:
    return TokenService()


def test_create_access_token_returns_valid_jwt(svc, sample_user_id):
    token = svc.create_access_token(sample_user_id)
    payload = svc.verify_access_token(token)

    assert payload["sub"] == str(sample_user_id)


def test_access_token_contains_exp_claim(svc, sample_user_id):
    token = svc.create_access_token(sample_user_id)
    payload = svc.verify_access_token(token)

    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)


def test_verify_expired_token_raises(rsa_key_pair):
    private_pem, _ = rsa_key_pair
    payload = {
        "sub": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc) - timedelta(hours=1),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(payload, private_pem, algorithm="RS256")

    with pytest.raises(jwt.ExpiredSignatureError):
        TokenService().verify_access_token(expired_token)


def test_verify_tampered_token_raises(svc, sample_user_id):
    token = svc.create_access_token(sample_user_id)
    tampered = token[:-10] + "AAAAAAAAAA"

    with pytest.raises(jwt.InvalidTokenError):
        svc.verify_access_token(tampered)


def test_generate_refresh_token_returns_raw_and_hash(svc):
    raw, token_hash = svc.generate_refresh_token()

    assert len(raw) > 32
    assert len(token_hash) == 64  # SHA-256 hex digest


def test_hash_refresh_token_is_deterministic(svc):
    raw = "some-opaque-token"
    assert svc.hash_refresh_token(raw) == svc.hash_refresh_token(raw)


def test_generate_refresh_token_hash_matches_raw(svc):
    raw, token_hash = svc.generate_refresh_token()
    assert svc.hash_refresh_token(raw) == token_hash


def test_refresh_token_expires_at_is_future(svc):
    expires_at = svc.refresh_token_expires_at()
    assert expires_at > datetime.now(timezone.utc)
