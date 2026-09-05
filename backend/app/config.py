from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./signal.db"
    twelvedata_api_key: str = ""

    # Signs auth tokens. Override in .env for anything but local use.
    jwt_secret: str = "dev-only-insecure-secret-change-me-in-production"

    # Cap the window of changes shown to a returning user, so a long absence
    # doesn't surface months of slow drift as if it were recent.
    lookback_cap_days: int = 30

    # A day is unusual if the move is this many std-devs past the stock's
    # recent daily volatility, or volume is this many times its recent average.
    price_sigma_threshold: float = 2.0
    volume_ratio_threshold: float = 2.0
    # Minimum prior days needed to define "normal"; below this, no signal fires.
    min_baseline_days: int = 5

    # How many recent bars define a stock's "normal" for the engine.
    baseline_bars: int = 30

    # Market proxy for the index-relative signal, and how far a market-adjusted
    # move must exceed the stock's own volatility to count.
    index_symbol: str = "SPY"
    index_sigma_threshold: float = 1.5
    # A flag is high-confidence (not just medium) once combined signal strength
    # reaches this. Minimum possible flagged score is 2.0 (two signals at threshold).
    high_confidence_score: float = 3.0


settings = Settings()
