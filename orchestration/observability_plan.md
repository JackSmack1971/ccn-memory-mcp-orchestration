# Observability Plan (OTel-first)

## Spans & Events
- Spans per step: authenticate, authorize, validate_schema, deterministic_commit, indexed_query, lineage_export.
- Events: `policy_eval`, `commit_appended`, `index_updated`, `delegated_query`, `compensation_invoked`.
- Attributes (mandatory): tenant_id, actor, operation, commit_id, lamport, bytes, policy_version, cache_hit, index_used.

## SLIs/SLOs
- Latency p50/p95/p99 by operation; error rate; compensation rate; replay rate; cache hit rate; lineage export latency.
- Alerts: p95>80% budget for 10m; deny-rate spike; DLQ growth; WAL fsync errors.

## Logs
- Structured JSON: AUTHZ_DECISION, WRITE_RESULT, QUERY_RESULT, LINEAGE_RESULT with correlation ids.

## Traces → Dashboards
- Operational (latency/throughput/policy/indices), Governance (lineage coverage, mean time to audit), Reliability (MTTR, retries).
