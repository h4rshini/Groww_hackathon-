from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./signal.db"
    twelvedata_api_key: str = ""

    # Cap the window of changes shown to a returning user, so a long absence
    # doesn't surface months of slow drift as if it were recent.
    lookback_cap_days: int = 30

    # A day is unusual if the move is this many std-devs past the stock's
    # recent daily volatility, or volume is this many times its recent average.
    price_sigma_threshold: float = 2.0
    volume_ratio_threshold: float = 2.0
    # Minimum prior days needed to define "normal"; below this, no signal fires.
    min_baseline_days: int = 5


settings = Settings()
