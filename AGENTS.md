# AGENTS.md: AI Collaboration Guide

This document provides essential context for AI models interacting with the **CCN Memory MCP** project. Adhering to these guidelines will ensure consistency, maintain code quality, and optimize agent performance.

> **Note**: This file should be placed at the root of your repository. More deeply-nested AGENTS.md files (e.g., in subdirectories) will take precedence for specific sub-areas of the codebase. Direct user prompts will always override instructions in this file.

---

## 1. Project Overview & Purpose

*   **Primary Goal:** To implement a **CCN Memory MCP (Model Context Protocol)** - a protocol-native memory substrate for multi-agent AI systems. This is a **versioned graph store** with deterministic commits, RBAC authorization, query optimization, lineage tracking, and observability, designed to eliminate "context failures" as the primary blocker to agent reliability.
    
*   **Business Domain:** AI Infrastructure, Multi-Agent Orchestration, Governance & Compliance, Applied Research

*   **Key Features:**
    1. **Deterministic Commits**: Content-addressed, immutable commits with Lamport timestamps and canonical JSON (JCS) for provenance
    2. **RBAC Authorization**: OAuth 2.1 authentication + OPA (Open Policy Agent) for deny-by-default access control
    3. **Low-Latency Queries**: In-memory indexes for fast node/edge lookups with optional external graph engine delegation
    4. **Lineage Tracking**: Complete audit trails via write-ahead log (WAL) with OpenLineage export support
    5. **Observability**: OpenTelemetry-first instrumentation for traces, metrics, and structured logs

*   **Success Metrics (SLOs)**:
    - Read latency (p95): < 25ms
    - Write latency (p95): < 40ms  
    - Policy evaluation (p95): < 5ms
    - Availability: 99.9%
    - Lineage coverage: > 95%

---

## 2. Core Technologies & Stack

*   **Languages:** 
    - **Python 3.11+** (service modules with asyncio)
    - **TypeScript/JavaScript ES2023** (MCP protocol implementation)
    - **Node.js 18+** (MCP SDK and testing)

*   **Frameworks & Runtimes:**
    - **FastAPI** (Python web framework)
    - **Pydantic** (data validation and settings)
    - **@modelcontextprotocol/sdk** (MCP protocol implementation)
    - **uvicorn** (ASGI server runtime)

*   **Databases:** 
    - **Append-only JSONL files** (WAL storage - primary system of record)
    - **In-memory indexes** (for fast queries)
    - **Optional external graph engine** (Neo4j/Memgraph for complex traversals - not in MVP)

*   **Key Libraries/Dependencies:**
    - **Python**: python-jose[cryptography] (JWT), httpx (HTTP client), jsonschema (validation), opentelemetry-api, opentelemetry-sdk, pytest, pytest-asyncio
    - **Node.js/TypeScript**: @modelcontextprotocol/sdk, jest, ts-node, @types/jest

*   **Infrastructure & Operations:**
    - **OPA (Open Policy Agent)** v0.68.0+ (authorization policies)
    - **OAuth 2.1 provider** (Auth0, Keycloak for JWT validation)
    - **OpenTelemetry collector** (traces/metrics/logs)
    - **Docker/Podman** (containerization)
    - **S3-compatible storage** (backup/snapshots)

*   **Package Managers:** 
    - **Python**: pip (standard), managed via `pyproject.toml`
    - **Node.js**: npm (standard), managed via `package.json`

*   **Platforms:** Linux containers (primary), development on macOS/Linux/Windows via Docker

---

## 3. Architectural Patterns & Structure

*   **Overall Architecture:** 
    - **Microservices architecture** with clear separation of concerns
    - **Orchestrated workflow pattern** with thin coordination layer
    - **WAL (Write-Ahead Log) as system of record** with derived in-memory indexes
    - **Hybrid query model**: Fast in-memory lookups (90% queries) + optional external graph delegation (10%)

*   **Directory Structure Philosophy:**
    ```
    /src                          # All production source code
      /protocol                   # MCP JSON-RPC server (stdio/SSE transport)
      /auth                       # OAuth 2.1 JWT validation service
      /authz                      # OPA authorization client
      /commit                     # Deterministic commit protocol (JCS, Lamport, nonce dedup)
      /query                      # In-memory indexes + query service
      /lineage                    # WAL scanning + OpenLineage export
      /telemetry                  # OpenTelemetry tracing, metrics, logging
    
    /tests                        # All test suites
      /unit                       # Fast, isolated unit tests
      /integration                # Service integration tests (Docker Compose)
      /e2e                        # End-to-end workflow validation
      /smoke                      # Project structure validation
    
    /docs                         # Documentation and operational guides
      /deployment                 # Deployment guide, Docker configs, Grafana dashboards
    
    /scripts                      # Development and operational scripts
      dev.sh                      # Local development loop
      snapshot_cron.sh            # Backup automation
    
    /config                       # Environment configuration files
    
    /orchestration                # Workflow specifications (atomic tasks, flow contracts)
    ```

*   **Module Organization:**
    - **Protocol Layer**: MCP tool handlers → delegates to services
    - **Authorization Layer**: JWT validation → OPA policy evaluation → resource access
    - **Core Layer**: Commit service (canonicalization + WAL append + index update)
    - **Query Layer**: In-memory index lookups with optional graph engine delegation
    - **Observability Layer**: Cross-cutting tracing, metrics, structured logging

*   **Common Patterns & Idioms:**
    - **Async/Await**: All I/O operations use Python's asyncio
    - **Idempotency**: Nonce-based deduplication for all writes
    - **Deny-by-Default**: All operations require explicit authorization
    - **Content-Addressed Storage**: SHA-256 commit IDs ensure determinism
    - **Lamport Timestamps**: Logical clocks for causality ordering
    - **Compensation Logic**: Index rebuilds, circuit breakers, graceful degradation
    - **TDD Methodology**: Write tests first, implement to green, refactor

---

## 4. Coding Conventions & Style Guide

*   **Formatting:**
    - **Python**: Follow PEP 8, 4-space indentation, max line length 100 characters
    - **TypeScript/JavaScript**: 2-space indentation, single quotes, trailing commas, max line length 100 characters
    - Use **Black** for Python (no configuration needed)
    - Use **Prettier** for TypeScript (automatic via editor integration)

*   **Naming Conventions:**
    - **Python**:
        - Variables, functions, methods: `snake_case`
        - Classes: `PascalCase`
        - Constants: `SCREAMING_SNAKE_CASE`
        - Private members: `_leading_underscore`
        - Files: `snake_case.py`
    - **TypeScript/JavaScript**:
        - Variables, functions: `camelCase`
        - Types, Interfaces, Classes: `PascalCase`
        - Constants: `SCREAMING_SNAKE_CASE`
        - Files: `camelCase.ts`, `PascalCase.tsx` (for components)

*   **API Design Principles:**
    - **Explicit over implicit**: Clear function signatures with type hints
    - **Fail-fast validation**: Validate inputs at API boundaries (JSON Schema strict mode)
    - **Idempotent operations**: All writes require nonces; reads are naturally idempotent
    - **Resource-based URLs**: RESTful paths for HTTP APIs (when applicable)
    - **Versioned schemas**: Include schema version in all data structures

*   **Documentation Style:**
    - **Python**: Use docstrings for all public functions/classes (Google style)
    - **TypeScript**: Use JSDoc comments for all exported functions/types
    - **Inline comments**: Explain "why", not "what" (code should be self-documenting)
    - Always document:
        - Function purpose
        - Parameter types and constraints
        - Return types
        - Exceptions/errors raised
        - Side effects (e.g., WAL writes, index updates)

*   **Error Handling:**
    - **Python**: 
        - Use custom exception classes (e.g., `AuthenticationError`, `AuthorizationError`, `ValidationError`)
        - Raise exceptions for unrecoverable errors
        - Use standard `try/except` blocks
        - Log exceptions with full context before re-raising
    - **TypeScript**:
        - Use standard Error classes with clear messages
        - Prefer explicit error returns over exceptions where appropriate
        - Always handle Promise rejections

*   **Forbidden Patterns:**
    - **NEVER** use `any` type in TypeScript unless absolutely justified (use `unknown` instead)
    - **DO NOT** hardcode secrets, API keys, or credentials (use environment variables)
    - **NEVER** use `eval()` or `exec()` for dynamic code execution
    - **DO NOT** use string interpolation for SQL/queries (use parameterized queries)
    - **NEVER** bypass authentication or authorization checks "temporarily"
    - **DO NOT** commit commented-out code (use git history instead)
    - **NEVER** ignore linter warnings without documented justification

---

## 5. Development & Testing Workflow

*   **Local Development Setup:**
    1. **Prerequisites**:
        ```bash
        # Install Python 3.11+
        python3 --version  # Verify >= 3.11
        
        # Install Node.js 18+
        node --version     # Verify >= 18.0
        
        # Install Docker/Podman
        docker --version   # Verify installation
        ```
    
    2. **Project Setup**:
        ```bash
        # Clone repository
        git clone <repo-url>
        cd ccn-memory-mcp
        
        # Install Python dependencies
        pip install -r requirements.txt
        # Or if using pyproject.toml
        pip install -e .
        
        # Install Node.js dependencies
        npm install
        
        # Verify project structure
        pytest tests/smoke/test_project_structure.py
        ```
    
    3. **Start Development Environment**:
        ```bash
        # Start all services (app, OPA, OTel collector)
        docker-compose -f docker-compose.dev.yml up -d
        
        # Or use the dev script
        ./scripts/dev.sh
        
        # Verify services are healthy
        curl http://localhost:8080/health
        ```

*   **Build Commands:**
    - **Python**: No explicit build step (interpreted language)
    - **TypeScript**: `npm run build` (compiles to JavaScript)
    - **Docker**: `docker build -t ccn-memory-mcp -f Dockerfile.dev .`

*   **Testing Commands:**
    
    **CRITICAL**: All new code MUST have corresponding unit tests. Test coverage target is 90%+.
    
    ```bash
    # Python unit tests
    pytest tests/unit/ -v --cov=src --cov-report=term-missing
    
    # TypeScript/Node.js tests
    npm test
    # Or for specific files
    npm test tests/unit/protocol/test_mcp_server.test.ts
    
    # Integration tests (requires Docker Compose)
    pytest tests/integration/ -v
    
    # End-to-end tests
    pytest tests/e2e/ -v
    
    # Run ALL tests (unit + integration + e2e)
    pytest tests/ -v
    npm test
    
    # Performance/load tests
    pytest tests/integration/test_slo_validation.py
    ```
    
    **Mocking Requirements**:
    - All tests MUST mock external dependencies:
        - OAuth provider (use mock JWKS server in `tests/fixtures/`)
        - OPA service (use mock policy responses)
        - External graph engines (not in MVP)
        - Network calls (use `httpx.MockTransport` for Python, `jest.fn()` for Node)
    - Test filenames: `test_*.py` (Python), `*.test.ts` or `*.spec.ts` (TypeScript)

*   **Linting/Formatting Commands:**
    
    **All code MUST pass linting and formatting checks before committing.**
    
    ```bash
    # Python linting
    ruff check src/ tests/        # Fast linter
    mypy src/                     # Type checking
    
    # Python formatting
    black src/ tests/             # Auto-format
    isort src/ tests/             # Sort imports
    
    # TypeScript linting
    npm run lint                  # ESLint
    npm run lint:fix              # Auto-fix issues
    
    # TypeScript type checking
    npm run typecheck             # tsc --noEmit
    ```

*   **CI/CD Process Overview:**
    - **GitHub Actions** workflow (`.github/workflows/ci.yml`)
    - **Triggers**: Push to any branch, pull requests to `main`
    - **Jobs**:
        1. **Lint**: ruff, mypy (Python), ESLint (TypeScript) - must pass
        2. **Test**: pytest (unit + integration), jest (TypeScript) - must pass
        3. **Build**: Docker image build - must succeed
    - **Status**: PR cannot merge until all checks are green
    - **Pipeline time target**: < 5 minutes for fast feedback

---

## 6. Git Workflow & PR Instructions

*   **Pre-Commit Checks:**
    ```bash
    # ALWAYS run before committing:
    
    # 1. Format code
    black src/ tests/
    isort src/ tests/
    npm run lint:fix
    
    # 2. Run linters
    ruff check src/ tests/
    mypy src/
    npm run lint
    
    # 3. Run tests
    pytest tests/unit/ -v
    npm test
    
    # 4. Verify no uncommitted changes remain
    git status
    ```

*   **Branching Strategy:**
    - **DO NOT** commit directly to `main` branch
    - Create feature branches: `feat/<feature-name>` or `fix/<bug-name>`
    - Branch from latest `main`: `git checkout -b feat/my-feature main`
    - Keep branches short-lived (< 3 days ideal)
    - Delete branches after merge

*   **Commit Messages:**
    
    Follow **Conventional Commits** specification:
    
    ```
    <type>(<scope>): <subject>
    
    <body>
    
    <footer>
    ```
    
    **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`
    
    **Examples**:
    ```bash
    feat(commit): implement nonce-based deduplication
    
    Add idempotency layer to commit service using nonce+hash
    as deduplication key. This prevents duplicate WAL entries
    when clients retry operations.
    
    Closes #42
    ```
    
    ```bash
    fix(auth): handle expired JWT tokens gracefully
    
    Return 401 with clear error message when token exp claim
    is in the past. Previously returned generic 500 error.
    
    Breaking changes: Error response format changed from
    {"error": "auth_failed"} to {"error": "token_expired", "expired_at": "..."}
    ```
    
    **Commit message checklist**:
    - [ ] Answers: What changed?
    - [ ] Answers: Why?
    - [ ] Notes any breaking changes
    - [ ] References related issues/PRs
    - [ ] Complete sentences ending with periods

*   **Pull Request (PR) Process:**
    1. **Before creating PR**:
        - Ensure branch is up-to-date with `main`
        - All tests pass locally
        - All linters pass
        - No merge conflicts
    
    2. **PR title**: Use Conventional Commits format
        ```
        feat(query): add support for graph traversal queries
        ```
    
    3. **PR description MUST include**:
        ```markdown
        ## Description
        Clear explanation of what this PR does and why.
        
        ## Testing Done
        - [ ] Unit tests added for new functionality
        - [ ] Integration tests pass
        - [ ] Manual testing completed: [describe]
        
        ## Breaking Changes
        None / [List any breaking changes]
        
        ## Checklist
        - [ ] Code follows project conventions
        - [ ] Tests added/updated
        - [ ] Documentation updated
        - [ ] Linters pass
        - [ ] Type checking passes
        ```
    
    4. **Review process**:
        - Address all review comments
        - Keep discussion focused and professional
        - Request re-review after making changes

*   **Force Pushes:**
    - **NEVER** use `git push --force` on `main` branch (protected)
    - Use `git push --force-with-lease` on feature branches only when necessary
    - Coordinate with team if rebasing shared feature branches

*   **Clean State:**
    - **You MUST leave your worktree in a clean state** after completing a task
    - No uncommitted changes
    - No untracked files (except legitimate new files to be committed)
    - No temporary build artifacts

---

## 7. Security Considerations

*   **General Security Practices:**
    - **Be security-conscious**: Consider potential vulnerabilities in every code change
    - **Least privilege**: Grant minimum necessary permissions
    - **Defense in depth**: Multiple layers of security (auth + authz + validation)
    - **Fail secure**: Default to deny on errors

*   **Sensitive Data Handling:**
    - **NEVER** hardcode secrets, API keys, credentials, or tokens in source code
    - Use environment variables for all secrets (configure in `config/` or `.env`)
    - **DO NOT** commit `.env` files or any files containing secrets
    - Use placeholder values in example configs (e.g., `OAUTH_CLIENT_SECRET=your_secret_here`)
    - Rotate secrets regularly and invalidate compromised credentials immediately

*   **Input Validation:**
    - **ALWAYS** validate all user inputs at API boundaries
    - Use JSON Schema strict validation (reject extra fields)
    - Sanitize strings to prevent injection attacks (SQL, NoSQL, command injection)
    - Validate data types, ranges, and formats
    - Enforce maximum lengths for strings and arrays
    - **NEVER** trust client-provided data

*   **Authentication & Authorization:**
    - **ALWAYS** authenticate requests using OAuth 2.1 JWT validation
    - **ALWAYS** authorize actions via OPA policy evaluation
    - Implement deny-by-default (explicit grants required)
    - Log all authentication failures and authorization denials
    - Token validation MUST verify:
        - Signature (RS256)
        - Expiration (`exp` claim)
        - Issuer (`iss` claim)
        - Audience (`aud` claim)

*   **Common Vulnerabilities to Avoid (OWASP API Top-10)**:
    - **API1: Broken Object Level Authorization** → OPA enforces resource-level access
    - **API2: Broken Authentication** → OAuth 2.1 + JWT signature validation
    - **API3: Excessive Data Exposure** → Schema-based response filtering
    - **API4: Lack of Resources & Rate Limiting** → Per-tenant quotas (future)
    - **API6: Mass Assignment** → JSON Schema strict validation
    - **API8: Injection** → Parameterized queries, input sanitization

*   **Audit & Compliance:**
    - All operations MUST log: actor, action, resource, decision, timestamp
    - Preserve audit trail integrity (WAL is append-only, immutable)
    - Support lineage export for audit reconstruction
    - GDPR compliance: Support redaction via tombstone commits (P2 feature)

*   **Dependency Management:**
    - Keep all dependencies up-to-date
    - Run security scanners: `pip-audit` (Python), `npm audit` (Node)
    - Review CVE reports for critical vulnerabilities
    - Pin dependency versions for reproducibility

---

## 8. Specific Instructions for AI Collaboration

*   **Contribution Guidelines:**
    - Follow the atomic task decomposition pattern (see `atomic-tasks-codex.md`)
    - Each task should be independently testable and reversible
    - Write tests first (TDD): red → green → refactor
    - Break large features into small, incremental PRs (< 500 lines changed ideal)
    - Each PR should have a clear acceptance criteria and pass/fail tests

*   **Tool Usage:**
    - For OAuth/JWT operations, use `python-jose` library (not `PyJWT`)
    - For HTTP clients, use `httpx` (not `requests`) for async support
    - For testing, use `pytest` fixtures for setup/teardown
    - For mocking, use `pytest-mock` (Python), `jest.fn()` (TypeScript)

*   **Context Management:**
    - For tasks > 5 files or > 50 lines changed, propose a detailed implementation plan first
    - Reference the specification (`Versioned_Graph_Store_Specification.md`) for requirements
    - Consult flow contracts (`flow_contracts.json`) for orchestration logic
    - Check atomic tasks (`atomic-tasks-codex.md`) for task dependencies

*   **Quality Assurance & Verification:**
    
    **CRITICAL**: You MUST run all relevant checks after making code changes. DO NOT report completion until all checks pass.
    
    **Verification checklist**:
    - [ ] All unit tests pass (`pytest tests/unit/`, `npm test`)
    - [ ] Integration tests pass (if modified)
    - [ ] Linters pass (ruff, mypy, ESLint)
    - [ ] Type checking passes (`mypy`, `npm run typecheck`)
    - [ ] Code coverage maintained or improved (>90% target)
    - [ ] Documentation updated (if public API changed)
    - [ ] No security vulnerabilities introduced
    
    **If tests fail**:
    1. Provide the FULL error output (stack trace, error messages)
    2. Do NOT guess at fixes - analyze the root cause
    3. Reference relevant code sections and test files
    4. Propose a specific fix with rationale

*   **Project-Specific Quirks/Antipatterns:**
    - **WAL is system of record**: Never modify WAL entries (append-only)
    - **Lamport timestamps**: Must monotonically increase within partition
    - **Nonce deduplication**: Use `nonce+content_hash` as composite key
    - **OPA policy cache**: 5-minute TTL, refetch on miss
    - **JSON canonicalization**: Use JCS (RFC 8785) for deterministic hashing
    - **Index rebuilds**: Always replay from WAL, never trust in-memory state
    - **Circuit breakers**: Deny-by-default on OPA unavailability
    
    **Known limitations (MVP scope)**:
    - No multi-writer support (single-writer per partition)
    - No streaming results (full result sets returned)
    - No pagination for large lineage exports
    - No external graph engine integration (deferred to P1)
    - No GDPR redaction logic (deferred to P2)

*   **Troubleshooting & Debugging:**
    - If tests fail, paste the **FULL stack trace** including:
        - Error type and message
        - File paths and line numbers
        - Variable values (sanitize secrets)
        - Relevant log entries with correlation IDs
    - Use OpenTelemetry traces to debug latency issues
    - Check structured logs for error context (JSON format)
    - Reference observability dashboards (Grafana) for SLO violations
    - Consult chaos recipes (`chaos_recipes.md`) for failure scenarios
    
    **Common issues**:
    - **OPA unavailable**: Check docker-compose, verify OPA container running
    - **WAL disk full**: Check volume mounts, run cleanup scripts
    - **JWT validation fails**: Verify JWKS endpoint accessible, check token claims
    - **Index out-of-sync**: Trigger rebuild from WAL (`scripts/rebuild_indexes.sh`)

*   **Parallel Task Execution:**
    - Tasks that modify different services can run in parallel
    - Tasks with no shared dependencies can execute concurrently
    - Use clear naming for logs to distinguish parallel task outputs
    - Coordinate on shared resources (WAL, indexes) via locking

*   **Pass/Fail Criteria:**
    - **Tests define the finish line**: Task is complete when:
        1. All acceptance tests pass (see atomic task acceptance criteria)
        2. All linters pass (no errors, no warnings)
        3. Type checkers pass (mypy, tsc --noEmit)
        4. CI pipeline is green
    - **Stop only when checks are green**: Do not move to next task with failing tests
    - **Performance targets met**: Verify SLO latencies in test output

*   **Breaking Down Large Work:**
    - Break features into atomic tasks (reference `atomic-tasks-codex.md`)
    - Each task should be:
        - **Independent**: Can be developed/tested in isolation
        - **Testable**: Has clear acceptance criteria
        - **Reversible**: Can be rolled back cleanly
        - **Small**: Ideally < 1 day of work
    - Create task dependency graph to identify parallelizable work
    - Submit each atomic task as a separate PR
    - Use feature flags for gradual rollouts

*   **Operational Guidelines:**
    - Reference reliability checklist (`reliability_checklist.md`) before declaring "done"
    - Register toil in toil register (`toil_register.md`) for future automation
    - Document rollback procedures for any changes affecting data persistence
    - Update deployment guide if configuration changes
    - Add chaos recipes for new failure modes discovered

---

## 9. Observability & Monitoring

*   **OpenTelemetry Instrumentation:**
    - Every service operation MUST emit spans
    - Required span attributes: `actor`, `operation`, `correlation_id`, `commit_id`, `lamport`
    - Record exceptions as span events before re-raising
    - Propagate trace context across service boundaries

*   **Structured Logging:**
    - Use JSON format for all logs
    - Include in every log entry: `timestamp`, `level`, `correlation_id`, `actor`, `service`, `message`
    - Log levels: DEBUG (detailed traces), INFO (normal ops), WARNING (potential issues), ERROR (failures), CRITICAL (service degradation)
    - Sample high-frequency logs (10% rate) to reduce volume

*   **Metrics & SLOs:**
    - Monitor SLO metrics continuously:
        - Latency histograms (p50, p95, p99)
        - Error rates by operation type
        - Authorization deny rates
        - Cache hit rates
        - WAL append throughput
    - Alert on SLO burn rate (> 0.001 = consuming 10% error budget/hour)
    - Dashboard specifications in `metrics_dashboard_spec.json`

*   **Health Checks:**
    - `/health` endpoint returns 200 OK when:
        - WAL is writable
        - Indexes are initialized
        - OPA is reachable
        - Memory usage < 80% threshold
    - Returns 503 Service Unavailable with detailed status on failure

---

## 10. Performance Expectations

When implementing features, always keep these performance targets in mind:

*   **Read Operations (memory.read, memory.search)**:
    - p95 latency: < 25ms (end-to-end)
    - Breakdown: Auth (2ms) + Authz (5ms) + Query (15ms) + Protocol overhead (3ms)
    - Optimization: Use in-memory indexes, avoid disk I/O

*   **Write Operations (memory.write)**:
    - p95 latency: < 40ms (end-to-end)
    - Breakdown: Auth (2ms) + Authz (5ms) + Canonicalization (5ms) + Hash (5ms) + WAL append (10ms) + Index update (5ms) + Protocol overhead (8ms)
    - Optimization: Batch index updates, use async I/O

*   **Policy Evaluation (OPA)**:
    - p95 latency: < 5ms
    - Use local OPA instance (not remote)
    - Cache policy decisions (5-minute TTL)
    - Deny-by-default on timeout

*   **Lineage Export**:
    - Direct lineage (100 commits): < 50ms
    - Full lineage (10K commits): < 2s
    - Use pagination for interactive use cases

*   **Throughput Targets**:
    - Reads: 10K req/sec per shard
    - Writes: 2K req/sec per shard
    - Scale horizontally via partitioning

---

## 11. Avoidances/Forbidden Actions

**DO NOT**:

- ❌ Modify committed WAL entries (append-only, immutable)
- ❌ Bypass authentication or authorization checks (even "temporarily")
- ❌ Use synchronous I/O in async functions (blocks event loop)
- ❌ Hardcode configuration values (use environment variables)
- ❌ Ignore test failures or skip flaky tests
- ❌ Use global mutable state (causes race conditions)
- ❌ Implement custom crypto (use standard libraries)
- ❌ Expose internal implementation details in public APIs
- ❌ Create circular dependencies between modules
- ❌ Use `print()` for logging (use structured logging)
- ❌ Commit large files (> 100KB) to git (use git-lfs or external storage)
- ❌ Implement features not in the specification without explicit approval
- ❌ Deploy without running full integration test suite
- ❌ Modify OPA policies without testing in isolated environment first

---

## 12. References

*   **Core Specification**: `Versioned_Graph_Store_Specification.md`
*   **Atomic Tasks**: `atomic-tasks-codex.md`
*   **Flow Contracts**: `flow_contracts.json`
*   **Observability Plan**: `observability_plan.md`
*   **Metrics Dashboard**: `metrics_dashboard_spec.json`
*   **Reliability Checklist**: `reliability_checklist.md`
*   **Toil Register**: `toil_register.md`
*   **WIP Policy**: `wip_policy.md`
*   **Chaos Recipes**: `chaos_recipes.md`
*   **Rollback Procedures**: `rollback.md`, `replay_backfill.md`
*   **Technical Rules**:
    - WAL Commit Protocol: `wal_commit_protocol_rules.md`
    - Cypher Performance: `cypher_performance_rules.md`
    - Neo4j Delegation: `neo_4_j_delegation_rules.md`
    - Boto3 Snapshot: `boto_3_snapshot_rules.md`
    - OpenTelemetry SDK: `otel_sdk_rules.md`
    - OPA Authorization: `opa_authz_rules.md`
    - JWT/JWKS Auth: `jwt_jwks_auth_rules.md`
    - Uvicorn Runtime: `uvicorn_runtime_rules.md`

---

## 13. Final Reminders

1. **TDD is non-negotiable**: Write tests first, then implement
2. **Security is everyone's responsibility**: Review code with security mindset
3. **Observability is built-in, not bolted-on**: Instrument as you code
4. **Documentation lives with code**: Update docs in same PR as code changes
5. **Performance matters**: Profile before optimizing, measure after changes
6. **Idempotency prevents chaos**: Use nonces, design for retries
7. **Fail-fast at boundaries**: Validate inputs early, fail clearly
8. **Clean code is maintainable code**: Simple beats clever
9. **Automation reduces toil**: Script repetitive tasks, update toil register
10. **Trust, but verify**: Run all checks, don't assume they pass

---

**Remember**: This document is a living guide. As you discover new patterns, edge cases, or best practices, propose updates via pull request. Your experience improves the project for everyone.

**Questions?** Refer to the specification, consult atomic tasks for context, and don't hesitate to ask clarifying questions before implementing.

**Success is measured by**: Code quality, test coverage, SLO adherence, security posture, and team velocity. Excellence in all five dimensions is the goal.
