"""The common envelope for one entry in the Operations Record.

Every producer (source adapter, anonymizer, summarizer, sparsifier, or the synthetic
example device) hands the aggregator objects of this one shape. The envelope is
normalized; the payload is not: it stays whatever the source naturally provides.

Times are integer seconds since the Unix epoch, UTC.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# Record classes from the proposal (Sec. 1.2).
RECORD_CLASSES = ("MS", "QA", "HI")  # machine state, quality assurance, human interpretation

# What a timestamp means for this entry.
#   state   - a value that holds from t_start until the next state entry of the same
#             type on the same element (t_end is None)
#   point   - something that happened at t_start
#   report  - a statement about [t_start, t_end] made by a person or a procedure
#   feature - a sparsified summary of bulk data over the window [t_start, t_end]
KINDS = ("state", "point", "report", "feature")

REVIEW_STATUSES = ("unreviewed", "proposed", "confirmed", "corrected", "rejected")

LINK_TYPES = ("direct", "indirect")
LINK_STATUSES = ("proposed", "confirmed", "corrected", "rejected")


@dataclass(frozen=True)
class Entry:
    """One entry, before it is stored.

    event time  = [t_start, t_end]: when the thing happened or held.
    known_at    = when the Record learned of it. A read "as of" time t only returns
                  entries with known_at <= t.
    """

    source: str               # originating system, e.g. "dcs", "dqm", "elog"
    record_class: str         # one of RECORD_CLASSES
    kind: str                 # one of KINDS
    type: str                 # source-specific type, e.g. "lv_voltage"
    element: str              # name of the detector element this entry is about
    t_start: int
    known_at: int
    t_end: Optional[int] = None
    payload: dict[str, Any] = field(default_factory=dict)
    raw_ref: str = ""         # pointer to the underlying source data (never a copy)
    producer: str = ""        # software or model that produced this entry
    producer_version: str = ""
    review_status: str = "unreviewed"

    def __post_init__(self) -> None:
        if self.record_class not in RECORD_CLASSES:
            raise ValueError(f"record_class {self.record_class!r} not in {RECORD_CLASSES}")
        if self.kind not in KINDS:
            raise ValueError(f"kind {self.kind!r} not in {KINDS}")
        if self.review_status not in REVIEW_STATUSES:
            raise ValueError(f"review_status {self.review_status!r} not in {REVIEW_STATUSES}")
        if self.t_end is not None and self.t_end < self.t_start:
            raise ValueError("t_end is before t_start")
        if self.known_at < self.t_start:
            raise ValueError("an entry cannot be known before it happened")
        if not self.producer:
            raise ValueError("every entry must name its producer")
