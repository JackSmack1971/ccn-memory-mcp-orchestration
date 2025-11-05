"""Unit tests for the JSONL WAL writer."""

from __future__ import annotations

import logging
import pathlib
from typing import List, NoReturn

import pytest

try:
    from src.storage import CommitEntry
    from src.storage.wal import WALAppendError, WALWriter
except ModuleNotFoundError:
    import sys
    from pathlib import Path as _Path
    PROJECT_ROOT = _Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from src.storage import CommitEntry
    from src.storage.wal import WALAppendError, WALWriter


@pytest.fixture()
def sample_entries() -> List[CommitEntry]:
    entries: List[CommitEntry] = [
        {
            "commit_id": "commit-1",
            "lamport_timestamp": 1,
            "payload": {"op": "create"},
        },
        {
            "commit_id": "commit-2",
            "lamport_timestamp": 2,
            "payload": {"op": "update"},
            "metadata": {"actor": "unit-test"},
        },
    ]
    return entries


def test_append_and_read_round_trip(tmp_path: pathlib.Path, sample_entries: List[CommitEntry]) -> None:
    writer = WALWriter(tmp_path)
    writer.append("partition-a", sample_entries[0])
    writer.append("partition-a", sample_entries[1])

    persisted = writer.read_range("partition-a", 0)
    assert persisted == sample_entries

    latest = writer.get_latest_lamport("partition-a")
    assert latest == sample_entries[-1]["lamport_timestamp"]


def test_read_range_offsets(tmp_path: pathlib.Path, sample_entries: List[CommitEntry]) -> None:
    writer = WALWriter(tmp_path)
    for entry in sample_entries:
        writer.append("partition-b", entry)

    second_entry_only = writer.read_range("partition-b", start_offset=1, end_offset=2)
    assert second_entry_only == [sample_entries[1]]

    trailing_entries = writer.read_range("partition-b", start_offset=1)
    assert trailing_entries == sample_entries[1:]


def test_append_wraps_os_error(tmp_path: pathlib.Path, sample_entries: List[CommitEntry], monkeypatch: pytest.MonkeyPatch) -> None:
    writer = WALWriter(tmp_path)

    def fail_open(self: pathlib.Path, *args: object, **kwargs: object) -> NoReturn:
        raise OSError("disk failure")

    monkeypatch.setattr(pathlib.Path, "open", fail_open)

    with pytest.raises(WALAppendError):
        writer.append("partition-c", sample_entries[0])


def test_rotation_warning_once(tmp_path: pathlib.Path, sample_entries: List[CommitEntry], caplog: pytest.LogCaptureFixture) -> None:
    writer = WALWriter(tmp_path, rotation_threshold_bytes=10)
    caplog.set_level(logging.WARNING)

    writer.append("partition-d", sample_entries[0])
    writer.append(
        "partition-d",
        {
            "commit_id": "commit-3",
            "lamport_timestamp": 3,
            "payload": {"op": "delete"},
        },
    )

    warnings = [record for record in caplog.records if "requires rotation" in record.getMessage()]
    assert len(warnings) == 1


def test_get_latest_lamport_missing_partition(tmp_path: pathlib.Path) -> None:
    writer = WALWriter(tmp_path)
    assert writer.get_latest_lamport("missing") == 0


def test_read_range_invalid_offsets(tmp_path: pathlib.Path) -> None:
    writer = WALWriter(tmp_path)
    with pytest.raises(ValueError):
        writer.read_range("partition-e", start_offset=-1)
    with pytest.raises(ValueError):
        writer.read_range("partition-e", start_offset=5, end_offset=1)
