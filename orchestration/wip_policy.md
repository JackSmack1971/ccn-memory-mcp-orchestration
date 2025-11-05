# WIP & Backpressure Policy

Target SLOs: read p95 <25ms; write p95 <40ms; authZ p95 <5ms.

Little’s Law sizing (per shard):
- Write: λ_w = 2000 req/s (target), W_w = 40ms → L_w ≈ 80 in system → set concurrency 128, queue_limit 2000.
- Read: λ_r = 10000 req/s, W_r = 25ms → L_r ≈ 250 → concurrency 512–1024, queue_limit 6000.

Policies:
- Strict limits per step (see flow_contracts.json).
- Admission control: shed load at 95% CPU or queue > 80% for 30s.
- Priority: authz/reads over lineage; lineage can be deferred.
- Circuit breakers: external graph delegation opens at 5 consecutive 200ms breaches; fallback to capped traversal.
