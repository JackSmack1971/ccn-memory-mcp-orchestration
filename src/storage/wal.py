"""File-backed WAL writer implementation with JSONL persistence."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Set

from .types import CommitEntry, WALProtocol

_LOGGER = logging.getLogger(__name__)


class WALAppendError(RuntimeError):
    """Raised when appending to the WAL fails due to an I/O issue."""


class WALWriter(WALProtocol):
    """Durable JSONL-based WAL writer with fsync guarantees."""

    def __init__(
        self,
        wal_directory: Path | str,
        *,
        rotation_threshold_bytes: int = 1_073_741_824,
    ) -> None:
        self._wal_directory = Path(wal_directory)
        self._rotation_threshold_bytes = rotation_threshold_bytes
        self._warned_partitions: Set[str] = set()
        self._wal_directory.mkdir(parents=True, exist_ok=True)

    def append(self, partition_id: str, entry: CommitEntry) -> None:
        """Persist an entry to the WAL using JSONL encoding with fsync durability."""

        self._validate_partition(partition_id)
        self._validate_entry(entry)
        partition_file = self._partition_path(partition_id)
        serialized = self._serialize_entry(entry)

        try:
            partition_file.parent.mkdir(parents=True, exist_ok=True)
            with partition_file.open("a", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:  # Security: never leak internal paths in errors
            raise WALAppendError(f"Failed to append WAL entry for partition '{partition_id}'") from exc

        self._maybe_warn_rotation(partition_id, partition_file)

    def read_range(
        self,
        partition_id: str,
        start_offset: int,
        end_offset: Optional[int] = None,
    ) -> List[CommitEntry]:
        """Read entries within the specified offsets for a partition."""

        self._validate_partition(partition_id)
        if start_offset < 0:
            raise ValueError("start_offset must be non-negative")
        if end_offset is not None and end_offset < start_offset:
            raise ValueError("end_offset must be greater than or equal to start_offset")

        partition_file = self._partition_path(partition_id)
        if not partition_file.exists():
            return []

        entries: List[CommitEntry] = []
        try:
            with partition_file.open("r", encoding="utf-8") as handle:
                for index, line in enumerate(handle):
                    if index < start_offset:
                        continue
                    if end_offset is not None and index >= end_offset:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    if not isinstance(data, dict):
                        raise ValueError("Malformed WAL entry: expected object")
                    entries.append(self._coerce_entry(data))
        except json.JSONDecodeError as exc:
            raise ValueError("Malformed WAL entry encountered during read") from exc
        except OSError as exc:
            raise WALAppendError(f"Failed to read WAL entries for partition '{partition_id}'") from exc

        return entries

    def get_latest_lamport(self, partition_id: str) -> int:
        """Return the highest Lamport timestamp recorded for the partition."""

        self._validate_partition(partition_id)
        partition_file = self._partition_path(partition_id)
        if not partition_file.exists():
            return 0

        try:
            last_line = self._read_last_non_empty_line(partition_file)
        except OSError as exc:
            raise WALAppendError(
                f"Failed to inspect WAL entries for partition '{partition_id}'"
            ) from exc

        if last_line is None:
            return 0

        try:
            payload = json.loads(last_line)
        except json.JSONDecodeError as exc:
            raise ValueError("Malformed WAL entry encountered while seeking latest Lamport") from exc

        if not isinstance(payload, dict):
            raise ValueError("Malformed WAL entry encountered while seeking latest Lamport")

        entry = self._coerce_entry(payload)
        return entry["lamport_timestamp"]

    def _partition_path(self, partition_id: str) -> Path:
        return self._wal_directory / f"{partition_id}.jsonl"

    def _validate_partition(self, partition_id: str) -> None:
        if not partition_id or not partition_id.strip():
            raise ValueError("partition_id must be a non-empty string")

    def _validate_entry(self, entry: CommitEntry) -> None:
        if not entry.get("commit_id"):
            raise ValueError("commit_id must be provided")
        lamport = entry.get("lamport_timestamp")
        if not isinstance(lamport, int) or lamport < 0:
            raise ValueError("lamport_timestamp must be a non-negative integer")
        payload = entry.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary")
        metadata = entry.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be a dictionary when provided")

    def _serialize_entry(self, entry: CommitEntry) -> str:
        return json.dumps(entry, separators=(",", ":"), sort_keys=True, ensure_ascii=False)

    def _coerce_entry(self, raw: dict[str, object]) -> CommitEntry:
        commit_id = raw.get("commit_id")
        lamport = raw.get("lamport_timestamp")
        payload = raw.get("payload")
        metadata = raw.get("metadata")

        if not isinstance(commit_id, str):
            raise ValueError("Malformed WAL entry: commit_id must be a string")
        if not isinstance(lamport, int):
            raise ValueError("Malformed WAL entry: lamport_timestamp must be an integer")
        if lamport < 0:
            raise ValueError("Malformed WAL entry: lamport_timestamp must be non-negative")
        if not isinstance(payload, dict):
            raise ValueError("Malformed WAL entry: payload must be a dictionary")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("Malformed WAL entry: metadata must be a dictionary when provided")

        coerced: CommitEntry = {
            "commit_id": commit_id,
            "lamport_timestamp": lamport,
            "payload": payload,
        }
        if metadata is not None:
            coerced["metadata"] = metadata
        return coerced

    def _read_last_non_empty_line(self, path: Path) -> Optional[str]:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            position = handle.tell()
            if position == 0:
                return None

            buffer = bytearray()
            while position > 0:
                position -= 1
                handle.seek(position)
                byte = handle.read(1)
                if byte == b"\n":
                    if buffer:
                        break
                    continue
                buffer.extend(byte)
            if not buffer:
                handle.seek(0)
                first_line = handle.readline()
                return first_line.decode("utf-8").strip() or None
            buffer.reverse()
            return buffer.decode("utf-8")

    def _maybe_warn_rotation(self, partition_id: str, partition_file: Path) -> None:
        try:
            size = partition_file.stat().st_size
        except OSError:
            return

        if size > self._rotation_threshold_bytes and partition_id not in self._warned_partitions:
            self._warned_partitions.add(partition_id)
            _LOGGER.warning(
                "Partition %s WAL has reached %d bytes and requires rotation", partition_id, size
            )
            # Rotation logic intentionally deferred for follow-up implementation
