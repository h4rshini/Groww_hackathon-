from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TickerRequest(BaseModel):
    symbol: str


class WatchlistItemOut(BaseModel):
    symbol: str
    name: str | None
    added_at: datetime
    # Null right after adding, until the background fetch fills it in.
    latest_close: float | None
    latest_date: date | None


class FeedEntry(BaseModel):
    symbol: str
    name: str | None
    confidence: str
    score: float
    reasons: list[str]
    flagged_on: date
    latest_close: float | None
    # Plain context, not a signal: percent change since the user's last visit.
    since_last_seen_pct: float | None


class FeedResponse(BaseModel):
    last_seen_at: datetime | None
    window_days: int
    items: list[FeedEntry]
