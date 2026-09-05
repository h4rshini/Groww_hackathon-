from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .deps import get_current_user, get_db
from .models import ChangeEvent, Instrument, Observation, User, WatchlistItem
from .schemas import FeedEntry, FeedResponse

router = APIRouter(tags=["feed"])


def _utcnow() -> datetime:
    # Naive UTC, to match the datetimes stored by the DB default.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _window_days(last_seen: datetime | None) -> int:
    if last_seen is None:
        return settings.lookback_cap_days
    gap = (_utcnow() - last_seen).days
    return min(max(gap, 0), settings.lookback_cap_days)


def _latest(db: Session, instrument_id: int) -> Observation | None:
    return db.scalar(
        select(Observation)
        .where(Observation.instrument_id == instrument_id)
        .order_by(Observation.bar_date.desc())
        .limit(1)
    )


def _since_last_seen_pct(db, instrument_id, last_seen, latest) -> float | None:
    if last_seen is None or latest is None:
        return None
    baseline = db.scalar(
        select(Observation)
        .where(
            Observation.instrument_id == instrument_id,
            Observation.bar_date <= last_seen.date(),
        )
        .order_by(Observation.bar_date.desc())
        .limit(1)
    )
    if baseline is None or baseline.close == 0:
        return None
    return round((latest.close - baseline.close) / baseline.close * 100, 1)


@router.get("/feed", response_model=FeedResponse)
def get_feed(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    last_seen = user.last_seen_at
    window_days = _window_days(last_seen)
    cutoff = date.today() - timedelta(days=window_days)

    watched = db.scalars(
        select(WatchlistItem.instrument_id).where(WatchlistItem.user_id == user.id)
    ).all()

    entries: list[FeedEntry] = []
    for instrument_id in watched:
        event = db.scalar(
            select(ChangeEvent)
            .where(
                ChangeEvent.instrument_id == instrument_id,
                ChangeEvent.window_end >= cutoff,
            )
            .order_by(ChangeEvent.window_end.desc(), ChangeEvent.score.desc())
            .limit(1)
        )
        if event is None:
            continue
        inst = db.get(Instrument, instrument_id)
        latest = _latest(db, instrument_id)
        entries.append(FeedEntry(
            symbol=inst.symbol,
            name=inst.name,
            confidence=event.confidence,
            score=event.score,
            reasons=event.reasons,
            flagged_on=event.window_end,
            latest_close=latest.close if latest else None,
            since_last_seen_pct=_since_last_seen_pct(db, instrument_id, last_seen, latest),
        ))

    entries.sort(key=lambda e: e.score, reverse=True)
    return FeedResponse(last_seen_at=last_seen, window_days=window_days, items=entries)


@router.post("/seen")
def mark_seen(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.last_seen_at = _utcnow()
    db.commit()
    return {"last_seen_at": user.last_seen_at}
