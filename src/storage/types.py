"""Type definitions and protocols for WAL storage components."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol, TypedDict, runtime_checkable, NotRequired


class CommitEntry(TypedDict):
    """Typed representation of a commit persisted in the WAL."""

    commit_id: str
    lamport_timestamp: int
    payload: dict[str, Any]
    metadata: NotRequired[dict[str, Any]]


@runtime_checkable
class WALProtocol(Protocol):
    """Interface that all WAL implementations must follow."""

    def append(self, partition_id: str, entry: CommitEntry) -> None:
        """Persist a commit entry for the provided partition."""

    def read_range(
        self,
        partition_id: str,
        start_offset: int,
        end_offset: Optional[int] = None,
    ) -> List[CommitEntry]:
        """Read a contiguous range of entries for the partition."""

    def get_latest_lamport(self, partition_id: str) -> int:
        """Return the latest Lamport timestamp recorded for the partition."""
