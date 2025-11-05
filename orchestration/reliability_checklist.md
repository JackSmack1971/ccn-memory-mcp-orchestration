# Ship Checklist (10-point)

1) Idempotent? Keys on nonce+hash; WAL as SoR; duplicate-safe writes — PASS (tests FR-002).  
2) Durable state? WAL+replay; deterministic resume — PASS.  
3) Compensations? Index rebuild; cancel external query; tombstones for GDPR — PASS/Partially (redaction flows P2).  
4) Thin orchestrator? Coordination only; business logic in services — PASS.  
5) Observability? OTel spans/events/logs, SLIs/SLOs wired — PASS.  
6) Backpressure/WIP? Concurrency caps; queue bounds; Little’s Law sizing — PASS.  
7) Rollout metrics? Four Keys + MTTR dashboards & alerts — PASS (operationalized).  
8) Toil review? Register below & tickets opened — IN PROGRESS.  
9) Failure drills? Crash, duplicate, partition, OPA slowness, schema drift — SCHEDULED.  
10) Orch vs choreo documented? Boundaries & rationale — PASS.
