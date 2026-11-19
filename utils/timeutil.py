"""Time helpers. All Record times are integer seconds since the Unix epoch, UTC."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

MINUTE = 60
HOUR = 3600
DAY = 86400


def to_iso(t: Optional[int]) -> str:
    """Epoch seconds -> '2040-03-01T02:00:00Z'. None -> '-'."""
    if t is None:
        return "-"
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso(s: str) -> int:
    """'2040-03-01T02:00:00Z', '2040-03-01T02:00' or '2040-03-01' -> epoch seconds (UTC)."""
    s = s.strip().replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return int(datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    raise ValueError(f"cannot read time {s!r}; use e.g. 2040-03-01T02:00")


def overlaps(a0: int, a1: Optional[int], b0: int, b1: int) -> bool:
    """True if [a0, a1] overlaps [b0, b1]. a1 None means a single instant at a0."""
    return a0 <= b1 and (a1 if a1 is not None else a0) >= b0
