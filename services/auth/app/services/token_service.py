import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from settings import settings


class TokenService:
    def create_access_token(self, user_id: uuid.UUID, email: str, is_admin: bool = False) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "email": email,
            "is_admin": is_admin,
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        }
        return jwt.encode(payload, settings.private_key, algorithm="RS256")

    def verify_access_token(self, token: str) -> dict:
        return jwt.decode(token, settings.public_key, algorithms=["RS256"])

    def generate_refresh_token(self) -> tuple[str, str]:
        """Returns (raw_token, sha256_hex_hash)."""
        raw = secrets.token_urlsafe(64)
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        return raw, token_hash

    def hash_refresh_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def refresh_token_expires_at(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
