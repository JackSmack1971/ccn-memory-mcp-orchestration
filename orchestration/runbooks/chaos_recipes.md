# Chaos & Failure Drills

- Mid-commit crash: kill after WAL append before index update → expect index_rebuild compensation.
- OPA latency spike: inject 50ms delay → verify deny+alert, p95 read stays <25ms by short-circuit.
- Duplicate delivery: resend identical write (same nonce) 100x → expect one WAL entry.
- External graph outage: 500s for 60s → breaker opens; queries degrade to capped traversal.
- Schema drift: remove required field → validation rejects with JSON-RPC -32602.
