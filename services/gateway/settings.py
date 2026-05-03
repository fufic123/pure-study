from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    public_key_path: Path = Path("keys/public.pem")

    redis_url: str = "redis://redis:6379/0"

    auth_service_url: str = "http://auth:8001"
    graph_service_url: str = "http://graph:8002"
    ai_service_url: str = "http://ai:8003"
    material_service_url: str = "http://material:8004"
    check_service_url: str = "http://check:8005"

    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    @property
    def public_key(self) -> str:
        if not self.public_key_path.exists():
            raise FileNotFoundError(
                f"RSA public key not found at '{self.public_key_path}'. "
                "Generate with: openssl rsa -in keys/private.pem -pubout -out keys/public.pem"
            )
        return self.public_key_path.read_text().strip()


settings = Settings()
