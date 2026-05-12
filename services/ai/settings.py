from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""

    material_service_url: str = "http://material:8004"
    graph_service_url: str = "http://graph:8002"

    copilot_history_trim_after: int = 10
    copilot_history_keep_last: int = 4


settings = Settings()
