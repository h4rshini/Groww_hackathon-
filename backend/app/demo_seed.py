"""Populate a demo account with sample tickers and a couple of example flags,
so the UI is explorable without waiting for a live market event. Used by the
seed_demo.py CLI and, on hosted deploys, on startup.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .config import settings
from .fetcher import FetchError, get_or_create_instrument, refresh_symbol
from .models import ChangeEvent, User, WatchlistItem
from .security import hash_password

SYMBOLS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"]
DEMO_PASSWORD = "password123"


def _flag(session, inst, days_ago, confidence, score, reasons):
    session.query(ChangeEvent).filter_by(instrument_id=inst.id).delete()
    d = date.today() - timedelta(days=days_ago)
    session.add(ChangeEvent(
        instrument_id=inst.id, window_start=d - timedelta(days=20), window_end=d,
        confidence=confidence, score=score, reasons=reasons,
    ))


def seed_demo_account(session: Session, email: str, create_user: bool = False) -> bool:
    user = session.query(User).filter_by(email=email).first()
    if user is None:
        if not create_user:
            return False
        user = User(email=email, password_hash=hash_password(DEMO_PASSWORD))
        session.add(user)
        session.flush()

    # A recent last-look so "since you last looked" has something to compare.
    user.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)

    insts = {}
    for sym in SYMBOLS:
        inst = get_or_create_instrument(session, sym)
        insts[sym] = inst
        if not session.query(WatchlistItem).filter_by(user_id=user.id, instrument_id=inst.id).first():
            session.add(WatchlistItem(user_id=user.id, instrument_id=inst.id))
        try:
            refresh_symbol(session, sym)
        except FetchError:
            pass
    try:
        refresh_symbol(session, settings.index_symbol)
    except FetchError:
        pass
    session.commit()

    _flag(session, insts["NVDA"], 1, "high", 12.0,
          ["Price moved up 3.6x its typical daily range",
           "Volume was 4.1x its recent average",
           "Moved 3.1x its typical range independent of the market"])
    _flag(session, insts["TSLA"], 3, "medium", 2.6,
          ["Price moved down 2.3x its typical daily range", "Volume was 2.2x its recent average"])
    session.commit()
    return True
