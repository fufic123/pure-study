from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Timeouts for external source requests (seconds)
    fetch_timeout: int = 15


settings = Settings()
