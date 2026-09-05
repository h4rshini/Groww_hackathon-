from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./signal.db"
    twelvedata_api_key: str = ""

    # Cap the detection window so a long-absent user doesn't get months of
    # slow drift reported as a sudden change.
    lookback_cap_days: int = 30


settings = Settings()
