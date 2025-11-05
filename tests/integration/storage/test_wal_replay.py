"""Integration tests verifying WAL replay semantics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

try:
    from src.storage import CommitEntry
    from src.storage.wal import WALWriter
except ModuleNotFoundError:
    import sys
    from pathlib import Path as _Path
    PROJECT_ROOT = _Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from src.storage import CommitEntry
    from src.storage.wal import WALWriter


@pytest.fixture()
def wal_entries() -> List[CommitEntry]:
    entries: List[CommitEntry] = [
        {
            "commit_id": "integration-1",
            "lamport_timestamp": 10,
            "payload": {"stage": "ingest"},
        },
        {
            "commit_id": "integration-2",
            "lamport_timestamp": 11,
            "payload": {"stage": "canonicalize"},
        },
        {
            "commit_id": "integration-3",
            "lamport_timestamp": 12,
            "payload": {"stage": "index"},
        },
    ]
    return entries


def test_wal_replay_recovers_entries(tmp_path: Path, wal_entries: List[CommitEntry]) -> None:
    wal_dir = tmp_path / "wal"
    writer = WALWriter(wal_dir)
    for entry in wal_entries:
        writer.append("partition-1", entry)

    replay_writer = WALWriter(wal_dir)
    replayed = replay_writer.read_range("partition-1", start_offset=0)
    assert replayed == wal_entries

    assert replay_writer.get_latest_lamport("partition-1") == wal_entries[-1]["lamport_timestamp"]


def test_wal_replay_detects_corruption(tmp_path: Path, wal_entries: List[CommitEntry]) -> None:
    wal_dir = tmp_path / "wal"
    wal_dir.mkdir(parents=True, exist_ok=True)
    partition_file = wal_dir / "partition-2.jsonl"
    valid_line = json.dumps(wal_entries[0], separators=(",", ":"), sort_keys=True)
    corrupt_line = "{\"commit_id\": \"bad\"}"
    partition_file.write_text(f"{valid_line}\n{corrupt_line}\n", encoding="utf-8")

    replay_writer = WALWriter(wal_dir)
    with pytest.raises(ValueError):
        replay_writer.read_range("partition-2", start_offset=0)

    with pytest.raises(ValueError):
        replay_writer.get_latest_lamport("partition-2")
