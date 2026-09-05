from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .engine import evaluate_instrument
from .fetcher import FetchError, refresh_symbol
from .models import Instrument, WatchlistItem


def refresh_watched(session: Session) -> dict:
    """Fetch latest bars and re-evaluate every instrument someone watches.

    Failures are isolated per instrument so one bad symbol or a rate limit
    doesn't abort the whole run.
    """
    # Keep the market proxy current so the index-relative signal has data.
    try:
        refresh_symbol(session, settings.index_symbol)
    except FetchError:
        pass

    instruments = session.scalars(
        select(Instrument)
        .join(WatchlistItem, WatchlistItem.instrument_id == Instrument.id)
        .distinct()
    ).all()

    fetched = flagged = errors = 0
    for inst in instruments:
        try:
            refresh_symbol(session, inst.symbol)
        except FetchError:
            errors += 1
            continue
        fetched += 1
        if evaluate_instrument(session, inst):
            flagged += 1

    return {"instruments": len(instruments), "fetched": fetched,
            "flagged": flagged, "errors": errors}
