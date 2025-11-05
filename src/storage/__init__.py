"""Storage abstractions for the write-ahead log (WAL)."""

from .types import CommitEntry, WALProtocol
from .wal import WALAppendError, WALWriter

__all__ = [
    "CommitEntry",
    "WALAppendError",
    "WALProtocol",
    "WALWriter",
]
