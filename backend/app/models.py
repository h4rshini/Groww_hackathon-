from datetime import datetime, date

from sqlalchemy import (
    String, Float, BigInteger, ForeignKey, DateTime, Date, JSON,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    # Cursor for "what changed since you last looked".
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["WatchlistItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


# Market data hangs off the instrument, not the user, so many watchers of the
# same stock share one set of bars and one computation.
class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="instrument", cascade="all, delete-orphan"
    )
    change_events: Mapped[list["ChangeEvent"]] = relationship(
        back_populates="instrument", cascade="all, delete-orphan"
    )


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "instrument_id", name="uq_user_instrument"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="items")
    instrument: Mapped["Instrument"] = relationship()


class Observation(Base):
    __tablename__ = "observations"
    # One bar per instrument per day, so a re-fetch updates instead of duplicating.
    __table_args__ = (
        UniqueConstraint("instrument_id", "bar_date", name="uq_instrument_bardate"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    bar_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(BigInteger)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    instrument: Mapped["Instrument"] = relationship(back_populates="observations")


class ChangeEvent(Base):
    __tablename__ = "change_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    window_start: Mapped[date] = mapped_column(Date)
    window_end: Mapped[date] = mapped_column(Date)
    confidence: Mapped[str] = mapped_column(String)  # "medium" | "high"
    score: Mapped[float] = mapped_column(Float)
    # Store the reasons at compute time so the UI can explain a flag without
    # recomputing it.
    reasons: Mapped[list] = mapped_column(JSON)

    instrument: Mapped["Instrument"] = relationship(back_populates="change_events")
