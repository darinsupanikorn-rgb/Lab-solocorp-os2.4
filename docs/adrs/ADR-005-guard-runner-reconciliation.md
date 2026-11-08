# ADR-005: Guard Runner Layer Architecture + Migration Scope

## Status
**Draft** — Mandated by CEO (หนุมาน) for completion within 24 hours.

## Context

Two issues converge requiring architectural reconciliation:

### Issue 1: Guard Runner — message-level vs project-level mismatch

The current `central_bus/guard_runner.py` is designed as a **project-level governance checker**. It loads guard specs from `gov/guards/*.toml`, loads project governance artifacts (ADRs, RFCs), and runs checkers against them for phase transitions. Its unit of work is the **project phase gate** — e.g., "Is ADR-001 signed off before Phase 3 can begin?"

The PRD-Central-Bus-v0.6 data flow assumes Guard Runner operates at **message-level** — an inline pre-route check that runs on every `POST /v1/observe` before a message is routed to its target department. The PRD flow diagram shows:

```
Agent → POST /observe → validate schema → INSERT INTO queue
  → Router Engine → match routing_rules → UPDATE status='routed'
  → Guard Runner → check pre-conditions → UPDATE status='guarded'
  → Return {queue_id, status, route_to}
```

This implies a check that completes in **milliseconds** per message, not a governance artifact scan that may take seconds and involve human-sign-off state.

**The conflict:** The existing `guard_runner.py` cannot serve inline message-level checks without major refactoring. But we also cannot discard it — project-level governance guards are required for pipeline phase gates. We need both, and they have fundamentally different latency and scope characteristics.

### Issue 2: Migration scope expansion

Current PRD-v0.6 migration scope is limited to `queue/*.jsonl`. CEO mandates migrating **all** bus data from JSONL/JSON files to SQLite. The full inventory of sources:

| Source | Format | Current Location |
|:-------|:-------|:-----------------|
| Queue messages | JSONL | `bus/queue/{priority}.jsonl` |
| Dead letters | JSONL | `bus/queue/dead_letter/{priority}.jsonl` |
| State files | JSON | `bus/projects/{id}/state.json` |
| Guard events | JSONL | `bus/governance/{project}/guard_events.jsonl` |
| Escalation log | JSONL | `bus/system/escalations.jsonl` |
| CEO alerts | JSONL | `bus/system/ceo_alerts.jsonl` |
| Audit logs | JSONL | `bus/projects/{project}/audit/{date}.jsonl` |

Each source has different schema, update patterns (append-only vs upsert), and volume characteristics. A single monolithic migration script risks bugs, partial failures, and difficult debugging.

---

## Decision

### Part 1: 2-Layer Guard Architecture

We adopt a **two-layer guard architecture** that separates the concerns of message-level inline checks from project-level governance checks.

#### Layer 1 — INLINE Guard (in bus daemon request path)

Runs synchronously inside the `POST /v1/observe` handler before routing. Must complete within **< 5ms** (budget: 5ms of the 100ms p99 API budget).

**Checks performed:**
1. **Schema validation** — Payload matches expected Pydantic schema (Message model)
2. **Source agent verification** — `agent_id` is a known, registered agent
3. **Rate limit check** — Per-agent throughput within configured limits (configurable in `routing_rules` table)
4. **Target validation** — `target_department` exists (or can be resolved via routing rules)

**Implementation:**
- New module: `central_bus/guards/inline.py`
- Accessed via a lightweight `InlineGuard` class instantiated per request
- Uses in-memory LRU caches (not SQLite reads) for:
  - Known agent list (refreshed every 60s from `facts` table)
  - Rate-limit counters (in-memory sliding window, written to SQLite every 30s for persistence)
- Failure action: Return HTTP 422 (validation) or HTTP 429 (rate-limit) — **blocks the request**

```
POST /v1/observe
  → InlineGuard.check(request)
     ├── schema_valid?        → 422 if fail
     ├── agent_known?         → 422 if fail
     ├── rate_ok?             → 429 if fail
     └── target_valid?        → 422 if fail
  → QueueManager.enqueue()
  → RouterEngine.route()
  → return {queue_id, status, route_to}
```

**Architecture diagram:**

```
┌──────────────────────────────────────────────────────────┐
│                  Bus Daemon (busd)                        │
│                    FastAPI / uvicorn                      │
│                                                          │
│  POST /v1/observe                                        │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────────────────┐                                │
│  │  Layer 1: INLINE     │  < 5ms budget                 │
│  │  ┌────────────────┐  │                                │
│  │  │ Schema validate │──┐                               │
│  │  │ Agent verify    │  │→ 422/429 if fail             │
│  │  │ Rate limit      │──┘                               │
│  │  │ Target valid    │                                  │
│  │  └────────────────┘                                   │
│  └─────────┬────────────────┘                            │
│            │ pass                                         │
│            ▼                                              │
│  ┌──────────────────────┐                                 │
│  │ Queue Manager        │                                 │
│  │ Router Engine        │                                 │
│  └─────────┬────────────┘                                 │
│            │ return {queue_id, route_to}                   │
│            ▼                                              │
│  ┌──────────────────────┐                                 │
│  │ Layer 2: ASYNC       │  fire-and-forget               │
│  │ GovernanceGuard      │  → audit_log + CRITICAL if fail│
│  │ PhaseGuard           │  → alert Orchestrator          │
│  │ SecurityGuard        │                                 │
│  └──────────────────────┘                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

#### Layer 2 — ASYNC Guard (background task in bus daemon)

Runs as a fire-and-forget background task **after** the message is queued and routed. No impact on API response time.

**Checks performed:**
1. **Governance guard** — Do the referenced project artifacts exist? Are required ADRs signed off?
2. **Phase constraint check** — Is the project ready for the phase implied by this message?
3. **Security/compliance checks** — Payload compliance with data policies, PII scanning (future)

**Implementation:**
- New module: `central_bus/guards/governance.py` — wraps the existing `guard_runner.py` logic
- Queued via `asyncio.create_task()` or a dedicated background thread pool
- Results written to `audit_log` table with severity levels:
  - `INFO` — Guard passed
  - `WARNING` — Non-blocking guard issue detected
  - `CRITICAL` — Guard failed (blocking should have been caught)
- On CRITICAL: also writes to `ceo_alerts` table and sets a flag in project state
- Does **not** block or roll back the original message — the message has already been routed

**Failure handling (CRITICAL):**
1. Write to `audit_log` with severity `CRITICAL` + full guard details
2. Write to `ceo_alerts` table for CEO dashboard visibility
3. Update project `state.json` with `guard_override_required: true` flag
4. Optionally: notify Orchestrator via dedicated alert channel

#### Existing `guard_runner.py` — Retained as Layer 2 backbone

The existing `guard_runner.py` remains untouched as the core engine for governance artifact checking. It is **not** called from Layer 1. Layer 2 wraps it asynchronously.

**Migration of existing code:**
- `central_bus/guard_runner.py` → `central_bus/guards/governance_checker.py` (renamed, preserved)
- New `central_bus/guards/__init__.py` exports `InlineGuard` and `GovernanceGuard`
- `central_bus/guards/inline.py` — new file for Layer 1
- `central_bus/guards/governance.py` — new file for Layer 2 orchestrator

#### Separation rationale

| Aspect | Layer 1 (INLINE) | Layer 2 (ASYNC) |
|--------|------------------|-----------------|
| **Latency budget** | < 5ms | No constraint (background) |
| **Blocks request?** | Yes (fail fast) | No (fire-and-forget) |
| **Data source** | In-memory cache, facts table | SQLite, governance TOML files |
| **Failure handling** | HTTP 422/429 to caller | audit_log CRITICAL + alert |
| **Existing code reuse** | None (new implementation) | Wraps existing guard_runner.py |
| **Unit of work** | Single message | Project context + governance state |
| **Guarantee** | Always runs (synchronous) | Best-effort (async, retry 3x) |

### Part 2: Migration Scope Expansion

#### Approach: Registry-based migration with per-source sub-scripts

Instead of a single monolithic `migrate.py`, we implement a **migration registry** where each data source is handled by its own sub-script. The registry tracks which sources have been migrated (idempotent).

#### SQLite schema additions

To the existing Central Bus v0.6 schema, add tracking columns to the `queue` and `audit_log` tables:

```sql
-- Add to queue table (existing)
ALTER TABLE queue ADD COLUMN src_type TEXT DEFAULT NULL;
  -- Values: 'queue_jsonl' | 'dead_letter_jsonl' | 'state_json' | 'guard_events_jsonl' | 'escalation_jsonl' | 'ceo_alerts_jsonl' | 'audit_jsonl'
ALTER TABLE queue ADD COLUMN src_path TEXT DEFAULT NULL;
  -- Original file path, e.g. 'bus/queue/high.jsonl' or 'bus/projects/PRJ-1/state.json'

-- Add to audit_log table (existing)
ALTER TABLE audit_log ADD COLUMN src_type TEXT DEFAULT NULL;
ALTER TABLE audit_log ADD COLUMN src_path TEXT DEFAULT NULL;
```

#### Migration registry

A JSON file `central_bus/migration_registry.json` tracks state:

```json
{
  "version": 1,
  "migrated_sources": {
    "queue_high": {"completed_at": "2026-07-05T10:00:00Z", "count": 142},
    "queue_normal": {"completed_at": "2026-07-05T10:01:30Z", "count": 89},
    "queue_low": {"completed_at": "2026-07-05T10:02:15Z", "count": 12},
    "dead_letter_high": {"completed_at": null, "count": 0},
    "dead_letter_normal": {"completed_at": null, "count": 0},
    "dead_letter_low": {"completed_at": null, "count": 0},
    "state_projects": {"completed_at": null, "count": 0},
    "guard_events": {"completed_at": null, "count": 0},
    "escalations": {"completed_at": null, "count": 0},
    "ceo_alerts": {"completed_at": null, "count": 0},
    "audit_logs": {"completed_at": null, "count": 0}
  }
}
```

#### Per-source migration sub-scripts

Each source gets its own sub-script in `central_bus/migration/`:

```
central_bus/
├── migrate.py                  # Entry point: reads registry, orchestrates sub-scripts
├── migration_registry.json     # Tracks completion state
└── migration/
    ├── __init__.py
    ├── base.py                 # Base class: validate, transform, insert, verify, mark_done
    ├── m001_queue.py           # Queue messages: bus/queue/{priority}.jsonl → queue table
    ├── m002_dead_letter.py     # Dead letters: bus/queue/dead_letter/{priority}.jsonl → dead_letter_queue
    ├── m003_state.py           # Project state: bus/projects/{id}/state.json → facts table
    ├── m004_guard_events.py    # Guard events: bus/governance/{project}/guard_events.jsonl → audit_log
    ├── m005_escalations.py     # Escalations: bus/system/escalations.jsonl → audit_log
    ├── m006_ceo_alerts.py      # CEO alerts: bus/system/ceo_alerts.jsonl → ceo_alerts table
    └── m007_audit_logs.py      # Audit logs: bus/projects/{project}/audit/{date}.jsonl → audit_log
```

**Each sub-script implements:**

```python
class MigrationSubScript:
    source_type: str           # Matches src_type value
    source_glob: str           # Glob pattern for files, e.g. "bus/queue/*.jsonl"
    target_table: str          # SQLite table name
    batch_size: int = 500      # Rows per INSERT

    def validate(line: dict) -> bool:
        """Validate a single record before insertion."""
        pass

    def transform(line: dict) -> dict:
        """Transform JSONL/JSON format → SQLite row dict."""
        pass

    def insert(rows: list[dict]) -> int:
        """Batch INSERT using aiosqlite."""
        pass

    def verify(count_before: int, count_after: int) -> bool:
        """Verify count matches. Logs warning on mismatch (non-blocking)."""
        pass
```

#### `migrate.py` entry point logic

```
migrate.py --all                # Migrate all pending sources
migrate.py --source queue       # Migrate only queue sources
migrate.py --source state       # Migrate only state files
migrate.py --status             # Show registry (what's done, what's pending)
migrate.py --reset              # Reset registry (for re-migration after schema changes)
```

Flow:
1. Load `migration_registry.json`
2. For each source with `completed_at == null` (or `--source` filter):
   a. Instantiate the corresponding sub-script
   b. Run `validate` → `transform` → `insert` in batches
   c. Run `verify` (count match, non-blocking warning)
   d. Mark `completed_at` in registry
3. Write updated registry

**Idempotency guarantee:**
- Registry prevents re-running completed migrations
- If a migration is partially complete (crash mid-way), re-running is safe because:
  - `INSERT OR IGNORE` with the original `id` as primary key for queue/dead-letter
  - State files use `key` (derived from project_id) as primary key in `facts` table
  - Audit logs use `id` as primary key with `INSERT OR IGNORE`

#### New SQLite tables for expanded scope

```sql
-- Escalation log (new table)
CREATE TABLE escalations (
    id              TEXT PRIMARY KEY,          -- UUID v4
    project_id      TEXT,
    source_agent    TEXT NOT NULL,
    severity        TEXT DEFAULT 'warning',    -- 'warning' | 'critical' | 'blocking'
    title           TEXT NOT NULL,
    detail          TEXT,                       -- JSON payload
    status          TEXT DEFAULT 'open',        -- 'open' | 'acknowledged' | 'resolved'
    assigned_to     TEXT,
    resolved_at     TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    src_type        TEXT,
    src_path        TEXT
);

-- CEO alerts (new table)
CREATE TABLE ceo_alerts (
    id              TEXT PRIMARY KEY,           -- UUID v4
    alert_type      TEXT NOT NULL,              -- 'guard_critical' | 'pipeline_failure' | 'system_error'
    severity        TEXT DEFAULT 'critical',
    source          TEXT NOT NULL,              -- which subsystem raised the alert
    title           TEXT NOT NULL,
    detail          TEXT,                       -- JSON payload
    acknowledged    INTEGER DEFAULT 0,
    acknowledged_by TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    src_type        TEXT,
    src_path        TEXT
);

-- Guard events (mapped from existing guard_runner output → audit_log with type='guard')
-- No new table: guard events → audit_log with action='guard.run' | 'guard.fail'
```

#### Migration dependency order

Sources are migrated in dependency order to preserve foreign-key-like references:

```
Order 1: Queue messages (no dependencies)
Order 2: Dead letters (references queue.id)
Order 3: Audit logs (independent, large volume)
Order 4: Guard events → audit_log
Order 5: Escalations
Order 6: CEO alerts
Order 7: State files → facts table (last, because state may reference queue/audit IDs)
```

---

## Consequences

### Positive

1. **Clear separation of concerns** — Inline guards (< 5ms) don't block on governance artifact loading. Governance guards don't degrade API latency.
2. **CEO mandate for full migration met** — All 7 source types migrated, not just queue.
3. **Idempotent, debuggable migration** — Per-source sub-scripts with registry tracking allow partial re-runs and clear status visibility.
4. **Existing code preserved** — `guard_runner.py` logic reused as Layer 2 backbone. No rewrite of working governance checks.
5. **Audit integrity** — Layer 2 failures still recorded in audit trail; no data loss even if governance guard fires late.
6. **Parallel migration possible** — Sub-scripts for different sources can run concurrently (no cross-dependencies except order 1→2).

### Negative

1. **Two guard files to maintain** — Inline guards and governance guards evolve independently, adding code surface area.
2. **Layer 2 false negatives possible** — If a message is routed and acted upon before Layer 2 runs, a CRITICAL guard finding creates a remediation event rather than a prevention.
3. **Migration complexity** — 7 sub-scripts + registry + verification logic is more code than a single script, though much safer.

### Trade-offs

| Trade-off | Option Chosen | Alternative |
|-----------|--------------|-------------|
| **Guard latency vs completeness** | Layer 1 = fast & shallow, Layer 2 = slow & deep | Single guard for both = latency unpredictable |
| **Migration simplicity vs safety** | Per-source sub-scripts + registry | Single monolithic script = harder to debug |
| **Backward compat during migration** | Registry + idempotent INSERT OR IGNORE | No compat = risk of data loss on partial run |
| **New tables vs overloaded existing** | New tables for escalations/ceo_alerts | Overloading queue/audit_log with mixed types = query complexity |
| **Async guard blocking vs non-blocking** | Fire-and-forget (non-blocking) | Synchronous governance guard = 100ms p99 risk |

---

## Appendix A: Migration Scope Summary

| # | Source | Current Location | Target Table | Sub-script | Records (est.) |
|:-:|:-------|:-----------------|:-------------|:-----------|:---------------|
| 1 | Queue (4 priorities) | `bus/queue/{p}.jsonl` | `queue` | `m001_queue.py` | ~500 |
| 2 | Dead letters (4 priorities) | `bus/queue/dead_letter/{p}.jsonl` | `dead_letter_queue` | `m002_dead_letter.py` | ~50 |
| 3 | Project state | `bus/projects/{id}/state.json` | `facts` | `m003_state.py` | ~30 |
| 4 | Guard events | `bus/governance/{project}/guard_events.jsonl` | `audit_log` | `m004_guard_events.py` | ~200 |
| 5 | Escalation log | `bus/system/escalations.jsonl` | `escalations` | `m005_escalations.py` | ~20 |
| 6 | CEO alerts | `bus/system/ceo_alerts.jsonl` | `ceo_alerts` | `m006_ceo_alerts.py` | ~10 |
| 7 | Audit logs | `bus/projects/{project}/audit/{date}.jsonl` | `audit_log` | `m007_audit_logs.py` | ~2000 |

**Total estimated records:** ~2,810
**Total sub-scripts:** 7
**Estimated migration time (all sources):** < 5 seconds on modern hardware

## Appendix B: File Map — New & Changed Files

```
NEW FILES:
central_bus/
├── guards/
│   ├── __init__.py              # Exports InlineGuard, GovernanceGuard
│   ├── inline.py                # Layer 1 — inline message guards
│   └── governance.py            # Layer 2 — async governance guard orchestrator
├── migration/
│   ├── __init__.py
│   ├── base.py                  # Abstract base class for migration sub-scripts
│   ├── m001_queue.py
│   ├── m002_dead_letter.py
│   ├── m003_state.py
│   ├── m004_guard_events.py
│   ├── m005_escalations.py
│   ├── m006_ceo_alerts.py
│   └── m007_audit_logs.py
└── migration_registry.json      # Tracks migration state per source

CHANGED FILES:
central_bus/
├── guard_runner.py              → central_bus/guards/governance_checker.py (renamed, preserved)
├── migrate.py                   ← Expanded to use registry + sub-scripts
├── db.py                        ← Add new tables + ALTER TABLE migrations
└── main.py                      ← Wire Layer 1 guards into POST /v1/observe
```

## Appendix C: Layer 2 CRITICAL Alert Flow

```
Layer 2 GovernanceGuard runs (async, fire-and-forget)
  │
  ├── Guard passes? → audit_log(severity=INFO) → Done
  │
  └── Guard fails?
      ├── audit_log(severity=WARNING) → Done (non-blocking issue)
      │
      └── Guard fails CRITICAL?
          ├── audit_log(severity=CRITICAL)
          ├── ceo_alerts.insert({alert_type: 'guard_critical', ...})
          ├── project state: guard_override_required = true
          └── Notify Orchestrator (via dedicated channel or alert endpoint)
```

---

*ADR-005 authored by Software Architect (พี่ทรงศักดิ์). Mandated by CEO (หนุมาน). Draft for review by Engineering (ช่างฟูล).*
