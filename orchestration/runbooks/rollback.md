# Rollback (Logical)

Scenario: bad index state post-deploy
1) Freeze writes.
2) Rebuild indexes from last good snapshot + WAL to current.
3) Health check queries.
4) Unfreeze writes; monitor p95.

Scenario: policy regression
1) Roll back OPA bundle to previous policy_version.
2) Purge cache; verify allow/deny samples.
