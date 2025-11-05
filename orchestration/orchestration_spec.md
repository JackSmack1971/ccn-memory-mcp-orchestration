# CCN Memory MCP — Orchestration Spec (MVP)

## Scope & SLAs
- MVP ships FR-001..FR-006 with SLOs: read p95 <25ms, write p95 <40ms, policy eval p95 <5ms, availability 99.9%. Source of truth: Specification v1.0.0. [derived]
- North Star: +20% task completion uplift post-deploy. [derived]

## Architecture & Boundaries
- Orchestrator: Temporal/Celery-lite coordinator (thin): sequences steps, enforces timeouts, retries (expo+jitter), emits spans; business logic stays in service modules.
- Services:
  - **ProtocolSvc** (MCP stdio/SSE, JSON-RPC, schema validation).
  - **AuthZSvc** (OAuth 2.1 validation, OPA PDP + policy cache).
  - **CommitSvc** (JCS canonicalize → hash → WAL append → Merkle link → index update).
  - **QuerySvc** (in-mem indexes; optional external graph delegation).
  - **LineageSvc** (history scan → export JSON/OpenLineage).
  - **Telemetry** (OTel traces/metrics/logs).
- Stores/Queues:
  - WAL (append-only JSONL on PV), Index RAM store, Policy cache, DLQ (failed steps), Snapshot bucket (S3).

## DAG (MVP Happy Path)
`ReceiveRequest → Authenticate → Authorize → ValidateSchema → DeterministicCommit (write) | IndexedQuery (read/search) → LineageExport (optional) → Respond`

### Write Path (UPSERT_NODE/EDGE, DELETE_*)
1. Authenticate (JWT verify, exp, iss). 
2. Authorize (OPA deny-by-default; cache; ≤5ms).
3. Validate (JSON Schema 2020-12).
4. Canonicalize (JCS) → Hash(SHA-256) → Lamport++ → Link(prev).
5. WAL Append (fsync) → Update indexes.
6. Return `{commit_id, lamport, ts}`.

Compensations:
- If WAL append succeeds but index update fails → **Rebuild index** from WAL range [prev+1..now]; idempotent.
- If OPA unavailable > timeout → **deny** (policy), emit incident; no side-effect to compensate.

### Read/Search Path
1. Authenticate → Authorize(READ/SEARCH) → Query indexes (≤25ms p95) or delegate to graph engine (≤200ms heavy). 
2. Include provenance (commit_id, actor, ts).

### Lineage Path
Scan WAL by entity partition → paginate/aggregate → export JSON/OpenLineage → stream to requester.

## SLAs/SLOs
- p95 latencies and availability from spec; alerts at 80% of budget (burn rates). [derived]

## RASCI
- **Responsible**: Platform Eng (service modules), SRE (infra), Security Arch (OAuth/OPA), Governance (policies), PM (rollout).
- **Accountable**: Tech Lead.
- **Consulted**: Applied Research.
- **Informed**: Stakeholders list (spec).

## Orchestration vs. Choreography
- Central orchestration across request lifecycle for visibility & compensations; internal modules emit events for optional choreo (indexer, lineage builder). Rationale: need auditability, exactly-once edges at boundaries. [derived]

## Failure Classes & Policies
- Auth failures → 401; AuthZ deny → 403 (deny-by-default).
- WAL append failure → retry w/ idempotency key; on partial success → replay idempotently.
- Index rebuild on divergence; query timeouts with graceful degradation to partial results.
- External graph delegation with circuit breaker; fallback to capped traversal.

## DR & Backfill
- Daily snapshots + WAL replay; RTO <15m, RPO <5m. Rebuild tasks are deterministic.

## Rollout
- Private beta behind feature flags; A/B for NSM uplift; red-team & OWASP API Top-10 gate.
