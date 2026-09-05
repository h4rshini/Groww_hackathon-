"""Populate a demo account with sample watched tickers and a couple of example
flags, so the UI can be explored without waiting for a live market event.

The engine still computes real flags on real data during normal use; this only
makes the demo account presentable. Usage: python seed_demo.py [email]
"""

import sys
from datetime import date, datetime, timedelta, timezone

from app.config import settings
from app.db import SessionLocal
from app.fetcher import FetchError, get_or_create_instrument, refresh_symbol
from app.models import ChangeEvent, User, WatchlistItem

EMAIL = sys.argv[1] if len(sys.argv) > 1 else "founder@signal.app"
SYMBOLS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"]


def flag(session, inst, days_ago, confidence, score, reasons):
    session.query(ChangeEvent).filter_by(instrument_id=inst.id).delete()
    d = date.today() - timedelta(days=days_ago)
    session.add(ChangeEvent(
        instrument_id=inst.id, window_start=d - timedelta(days=20), window_end=d,
        confidence=confidence, score=score, reasons=reasons,
    ))


def main():
    s = SessionLocal()
    user = s.query(User).filter_by(email=EMAIL).first()
    if not user:
        print(f"No user {EMAIL}. Register in the app first.")
        return

    # A recent last-look so "since you last looked" has something to compare.
    user.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)

    insts = {}
    for sym in SYMBOLS:
        inst = get_or_create_instrument(s, sym)
        insts[sym] = inst
        if not s.query(WatchlistItem).filter_by(user_id=user.id, instrument_id=inst.id).first():
            s.add(WatchlistItem(user_id=user.id, instrument_id=inst.id))
        try:
            refresh_symbol(s, sym)
        except FetchError as e:
            print(f"  fetch failed for {sym}: {e}")
    try:
        refresh_symbol(s, settings.index_symbol)  # market proxy for the index signal
    except FetchError as e:
        print(f"  index fetch failed: {e}")
    s.commit()

    flag(s, insts["NVDA"], 1, "high", 12.0,
         ["Price moved up 3.6x its typical daily range",
          "Volume was 4.1x its recent average",
          "Moved 3.1x its typical range independent of the market"])
    flag(s, insts["TSLA"], 3, "medium", 2.6,
         ["Price moved down 2.3x its typical daily range", "Volume was 2.2x its recent average"])
    s.commit()
    print(f"Seeded {EMAIL}: watching {', '.join(SYMBOLS)}, 2 example flags.")
    s.close()


if __name__ == "__main__":
    main()
