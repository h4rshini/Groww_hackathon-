from dataclasses import dataclass
from statistics import mean, stdev

from .config import settings


@dataclass
class SignalResult:
    name: str
    fired: bool
    value: float        # how far past normal, e.g. 2.3 (sigma) or 3.1 (x average)
    reason: str | None  # human-readable, set only when fired


def price_move_signal(closes: list[float]) -> SignalResult:
    """Latest daily return measured against the stock's own recent volatility.

    closes: daily closes, oldest first, latest last.
    """
    name = "price_move"
    # Need enough history for a meaningful baseline, plus today's move on top.
    if len(closes) < settings.min_baseline_days + 2:
        return SignalResult(name, False, 0.0, None)

    returns = [
        (closes[i] - closes[i - 1]) / closes[i - 1]
        for i in range(1, len(closes))
        if closes[i - 1] != 0
    ]
    today, baseline = returns[-1], returns[:-1]

    sigma = stdev(baseline)
    if sigma < 1e-9:  # perfectly flat history, nothing to measure against
        return SignalResult(name, False, 0.0, None)

    ratio = abs(today) / sigma
    if ratio < settings.price_sigma_threshold:
        return SignalResult(name, False, ratio, None)

    direction = "up" if today > 0 else "down"
    reason = f"Price moved {direction} {ratio:.1f}x its typical daily range"
    return SignalResult(name, True, ratio, reason)


def volume_signal(volumes: list[int]) -> SignalResult:
    """Latest volume against recent average volume. volumes oldest first, latest last."""
    name = "volume"
    if len(volumes) < settings.min_baseline_days + 1:
        return SignalResult(name, False, 0.0, None)

    today, baseline = volumes[-1], volumes[:-1]
    avg = mean(baseline)
    if avg <= 0:
        return SignalResult(name, False, 0.0, None)

    ratio = today / avg
    if ratio < settings.volume_ratio_threshold:
        return SignalResult(name, False, ratio, None)

    reason = f"Volume was {ratio:.1f}x its recent average"
    return SignalResult(name, True, ratio, reason)
