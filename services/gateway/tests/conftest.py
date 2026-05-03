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
(_keys_dir / "public.pem").write_text(TEST_PUBLIC_KEY)

os.environ["PUBLIC_KEY_PATH"] = str(_keys_dir / "public.pem")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# ── fixtures ───────────────────────────────────────────────────────────────────
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import jwt
import pytest


@pytest.fixture(scope="session")
def rsa_key_pair() -> tuple[str, str]:
    return TEST_PRIVATE_KEY, TEST_PUBLIC_KEY


@pytest.fixture(scope="session")
def sample_user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def valid_token(rsa_key_pair, sample_user_id) -> str:
    private_pem, _ = rsa_key_pair
    payload = {
        "sub": sample_user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


@pytest.fixture(scope="session")
def expired_token(rsa_key_pair) -> str:
    private_pem, _ = rsa_key_pair
    payload = {
        "sub": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc) - timedelta(hours=1),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return jwt.encode(payload, private_pem, algorithm="RS256")


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock()
    return redis
