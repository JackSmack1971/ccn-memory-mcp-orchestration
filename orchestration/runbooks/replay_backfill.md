# Replay & Backfill

## Replay a time window
1) Pause writers for partition. 
2) Restore snapshot T0 to staging → WAL replay T0..T1. 
3) Verify Merkle chain, index counts.
4) Promote indexes; resume writers.

## Backfill indexes from WAL
- Trigger job: read WAL range [C_start..C_end], rebuild in-memory structures.
- Idempotent: safe to rerun; uses commit_id watermarks.

## Validation
- Hash spot-check 1% of commits.
- p95 latency back to baseline before unfreeze.
