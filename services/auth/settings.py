from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pure_study"

    private_key_path: Path = Path("keys/private.pem")
    public_key_path: Path = Path("keys/public.pem")

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    frontend_url: str = "http://localhost:3000"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    @property
    def private_key(self) -> str:
        if not self.private_key_path.exists():
            raise FileNotFoundError(
                f"RSA private key not found at '{self.private_key_path}'. "
                "Generate with: openssl genrsa -out keys/private.pem 2048"
            )
        return self.private_key_path.read_text().strip()

    @property
    def public_key(self) -> str:
        if not self.public_key_path.exists():
            raise FileNotFoundError(
                f"RSA public key not found at '{self.public_key_path}'. "
                "Generate with: openssl rsa -in keys/private.pem -pubout -out keys/public.pem"
            )
        return self.public_key_path.read_text().strip()


settings = Settings()
