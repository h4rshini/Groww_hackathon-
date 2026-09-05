from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .deps import get_current_user, get_db
from .engine import evaluate_instrument
from .fetcher import FetchError, get_or_create_instrument, refresh_symbol
from .models import Instrument, Observation, User, WatchlistItem
from .schemas import TickerRequest, WatchlistItemOut

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _latest(db: Session, instrument_id: int) -> Observation | None:
    return db.scalar(
        select(Observation)
        .where(Observation.instrument_id == instrument_id)
        .order_by(Observation.bar_date.desc())
        .limit(1)
    )


def _to_out(db: Session, inst: Instrument, item: WatchlistItem) -> WatchlistItemOut:
    latest = _latest(db, inst.id)
    return WatchlistItemOut(
        symbol=inst.symbol,
        name=inst.name,
        added_at=item.added_at,
        latest_close=latest.close if latest else None,
        latest_date=latest.bar_date if latest else None,
    )


def backfill_symbol(symbol: str):
    """Fetch and evaluate a newly added symbol. Runs after the response, on its
    own session. A fetch failure just leaves the row empty for a later retry."""
    session = SessionLocal()
    try:
        inst = get_or_create_instrument(session, symbol)
        try:
            refresh_symbol(session, symbol)
        except FetchError:
            return
        evaluate_instrument(session, inst)
    finally:
        session.close()


@router.get("", response_model=list[WatchlistItemOut])
def list_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(WatchlistItem).where(WatchlistItem.user_id == user.id)).all()
    return [_to_out(db, db.get(Instrument, it.instrument_id), it) for it in items]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WatchlistItemOut)
def add_ticker(
    body: TickerRequest,
    bg: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    symbol = body.symbol.strip().upper()
    if not symbol:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "symbol required")

    inst = get_or_create_instrument(db, symbol)
    if db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == user.id,
            WatchlistItem.instrument_id == inst.id,
        )
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, "already in watchlist")

    item = WatchlistItem(user_id=user.id, instrument_id=inst.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    # The write is done; the vendor fetch happens after we respond.
    bg.add_task(backfill_symbol, symbol)
    return _to_out(db, inst, item)


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_ticker(
    symbol: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    symbol = symbol.strip().upper()
    inst = db.scalar(select(Instrument).where(Instrument.symbol == symbol))
    item = inst and db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == user.id,
            WatchlistItem.instrument_id == inst.id,
        )
    )
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "not in watchlist")
    db.delete(item)
    db.commit()
