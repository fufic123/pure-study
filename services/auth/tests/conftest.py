"""
Write temp .pem files and point settings at them before any import
can trigger Settings() instantiation in settings.py.
"""
import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

TEST_PRIVATE_KEY = _key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
).decode()

TEST_PUBLIC_KEY = _key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

_keys_dir = Path(tempfile.mkdtemp())
(_keys_dir / "private.pem").write_text(TEST_PRIVATE_KEY)
(_keys_dir / "public.pem").write_text(TEST_PUBLIC_KEY)

os.environ["PRIVATE_KEY_PATH"] = str(_keys_dir / "private.pem")
os.environ["PUBLIC_KEY_PATH"] = str(_keys_dir / "public.pem")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-secret")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost/auth/google/callback")

# ── fixtures ───────────────────────────────────────────────────────────────────
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from app.api.dtos.token_response import TokenResponse
from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.fixture(scope="session")
def rsa_key_pair() -> tuple[str, str]:
    return TEST_PRIVATE_KEY, TEST_PUBLIC_KEY


@pytest.fixture(scope="session")
def sample_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture(scope="session")
def valid_access_token(rsa_key_pair, sample_user_id) -> str:
    private_pem, _ = rsa_key_pair
    payload = {
        "sub": str(sample_user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_user(sample_user_id) -> MagicMock:
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "test@example.com"
    user.hashed_password = "$2b$12$fakehash"
    user.google_id = None
    return user


@pytest.fixture
def mock_refresh_token(sample_user_id) -> MagicMock:
    token = MagicMock(spec=RefreshToken)
    token.id = uuid.uuid4()
    token.user_id = sample_user_id
    token.revoked = False
    token.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    return token


@pytest.fixture
def token_response() -> TokenResponse:
    return TokenResponse(access_token="test-access", refresh_token="test-refresh")
