# SoloCorp OS 2.4 — Agent Quickstart

SoloCorp OS is an **organizational OS for AI agents and a modular MCP product**. The current repo contains docs-as-code (`profiles/*/SOUL.md`, `rules/`, `sop/`), the Central Bus service, the legacy Core MCP, and independent department MCP adapters. The approved product target is a local-first SoloCorp App with one CEO experience, a module registry, and a task queue. The target app is not implemented yet. Product direction and MVP scope live in [`docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md`](docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md). Authoritative roster: `profiles/INDEX.md`. Auto-loaded behavior context: `opencode.json` → `instructions` (`CLAUDE.md` + `rules/INDEX.md`).

## Start here

```
@rules/INDEX.md   ← 30-sec behavior map (6 files: receive, work, session, safety, env, certification)
```

## Current Product Direction — Owner-approved (2026-11-01)

- **Source of truth:** `docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md`. Use it for product target, MVP scope, sequencing, and deferred work.
- **Target:** Local-first SoloCorp App. Its host manages enabled department MCP connections; one CEO agent receives human briefs, routes work, and tracks task state through the registry and Central Bus queue.
- **Runtime companion:** docs/plans/SOLOCORP-APP-LOCAL-RUNTIME-DESIGN-v0.1.md records reversible implementation defaults and the Phase 1 build order.
- **Standalone requirement:** A department MCP remains usable by itself through an external compatible client. It must not require the CEO MCP or SoloCorp App for department-scoped capability.
- **MVP:** Local single-user app, explicit model/provider configuration, module toggles and health state, and one Content Creator end-to-end task path. Hosted multi-user service, billing, all departments, and a full autonomous worker pool are later phases.
- **Current implementation:** The Content Creator MCP pilot, Central Bus, and headless ModuleHost lifecycle groundwork exist. The first-party SoloCorp App shell/API, registry UI, provider flow, and product task workflow are **not implemented**. The pilot document is evidence, not proof that the app is complete.
- **Release assurance:** Production audit findings remain visible for pre-release work. They do not replace the MVP roadmap; never describe a known limitation as a passed production guarantee.
- **Content Creator standalone strategy (2026-11-02):** ADR-030 accepts the open-core boundary (MCP adapter open / content engine closed); ADR-031 keeps Sound Designer as a Content Creator specialist and Earshot as an internal dependency. Release remains free-first behind a quality floor, with signal-triggered monetization and 3 weekly metrics reviewed after 90 days (first: 2027-02-02). Split executes at PRD Phase 3, not as parallel work. Full reference: [Content MCP strategy](docs/plans/CONTENT-MCP-STRATEGY-v1.0.md).
- This repo has pre-existing untracked generated artifacts and work. Check `git status` and `git diff` before edits or commits; do not clean or overwrite unrelated files.

Default agent is `ceo-hanuman` (strategy + routing + final call). Owner (Dr.solodev) decides L5 only.

## Hierarchy + escalation (do-not-break)

```
Owner — L5: vision / org / core product ONLY
└── CEO (หนุมาน) — L4: strategy, cross-dept, roadmap
    └── COO (กิจ) — L3 gatekeeper: daily ops, L1–L3
        └── Department Heads — L2 · Loop Runner — L1 (auto)
```

- **Heads never implement** — they delegate to specialists.
- **Specialists never talk cross-department directly** — via Central Bus only (Control = Head-to-Head status/goals/handoffs; Data = code/designs/reports through the Bus).
- If Owner sees L1–L3 work, COO failed.

## Session protocol

- Start: `/bootstrap` (or `python scripts/session-bootstrap.py`) — injects health, brain, queue, git state.
- End: `/summary` (or `python scripts/session-summary.py --save`) — appends to `brain/session-log.md` (append-only; never rewrite history).
- Memory files are git-tracked: `brain/ceo-identity.md` (who), `brain/ceo-memory.json` (what), `brain/session-log.md` (history), `brain/learnt.md` (lessons).

## Cross-department workspaces (current manual client workflow)

- `/workspace [dept] [task]` (skill: `skills/@solocorp/cross-dept/dept-workspace/`) remains the manual OpenCode workflow for work that needs a separate agent session.
- In the planned SoloCorp App, the CEO can call tools from already-connected department MCPs in the same user conversation. That app behavior is a target, not an implemented feature yet.
- Human + visiting-agent manual: `docs/OPENCODE-GUIDE.md` (one file, both audiences).

## Python prep (required before any python work)

```bash
source .venv/bin/activate && export PYTHONPATH=.
```

CI uses **Python 3.12**. Run repo MCP servers with the project `.venv` and their documented module command. `SOLOCORP_API_KEY` applies to scoped Core MCP / API operations that require it; do not make it a dependency of standalone department MCPs.

## Services (only when bus-dependent work needs them)

| Service | Command | Port |
|:--------|:--------|:----:|
| Central Bus (busd) | `uvicorn central_bus.main:app --host 127.0.0.1 --port 8099` | 8099 |
| govctl API | `python -m govctl_cli api start` | 8765 |
| Loop Runner | `python -m loop_runner.main` | cron 30m |

**MCP servers load their code once at startup.** An edit afterwards is invisible
to the running process — a tool can answer from code that no longer exists.
Check `runtime.restart_required` in any `*_department_info()` response, or run
`scripts/restart-mcp.sh` (dry run by default, `--yes` to kill stale generations)
and the host respawns a fresh one on the next call.

## Test (CI's exact invocation — copy verbatim)

```bash
python -m pytest tests/ central_bus/tests/ --tb=short --cov-report=json:.coverage.json --no-header -q
python workers/auto_qa_gate.py --threshold=9 --project-id=auto-qa-pipeline --test-path="tests central_bus/tests"
```

- ⚠️ **Never run bare `pytest`** from root — profile-embedded tests abort collection and it misses `central_bus/tests/`. (`pytest.ini` defaults to `tests/` only; CI overrides with both paths.)
- Coverage baseline is **9** (intentionally low, CI-ready) — do not "fix" by raising it without an ADR.
- Evidence artifacts go to `bus/evidence/` (see SOP-06).

## Deploy / codegen

```bash
python3 scripts/build-profiles.py                    # build profiles (step 1 of /deploy)
python3 scripts/export-codex-agents.py               # export agents
python3 scripts/export-codex-agents.py --validate-only  # verify before commit
python3 scripts/validate-soul-profiles.py            # validate SOUL.md edits
```

Full flow lives in the `/deploy` command template in `opencode.json`.

## Safety (hard stops)

- **Never commit `.env`** (gitignored; seeded from `.env.example`). Mirror checks need a real `MAXPLUS_API_KEY`, not a placeholder.
- Bus runtime files are local-only — never commit `*.db-shm`, `*.db-wal`, logs, or `bus.db` state.
- `rm -rf`, `sudo`, `chown` are denied; `docker`, `rm`, `chmod` ask first. Outside-repo writes allowed only under `~/.hermes/**`, `~/.claude/**`, `~/.opencode/**`, `~/.config/opencode/**`, `/tmp/**` — anything else asks.
- **Inspect `git status` + `git diff` before every commit.** No destructive git/db ops without explicit confirmation.
- Prefer scoped tests and targeted edits over repo-wide refactors.

## Certification ladder (why "done" needs a checker)

From `rules/06-certification.md` (incident: work reported complete with zero code changed — checkers now mandatory):

- Order: **D1** (1-page why/which-agent/scope) → **D2** (50–150-line agent that really calls tools, with run output + exit code) → **D3** (≥20-task eval table: expected vs actual + root cause, no cherry-picking) → **D4** (someone else reproduces via runbook). Never skip.
- **Maker ≠ checker** every gate; default status is **NOT PASSED** until evidence is attached. Reporting "done" without evidence is the worst failure; reporting "blocked" with evidence is valid work.
- Registry: `profiles/CERTIFICATION-REGISTRY.md` (CEO/checker updates only). Before dispatching execution work, verify the agent is D2+.

## Key paths

| Path | What |
|:-----|:-----|
| `rules/` | Behavior rules — read before acting |
| `sop/` | Standard Operating Procedures (SOP-01–06) |
| `profiles/` | Department identities (`SOUL.md`); roster in `profiles/INDEX.md` |
| `central_bus/` | FastAPI daemon (30+ modules): queue, routing, mirror |
| `docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md` | Current product direction and MVP source of truth |
| `solocorp_mcp/` | Core MCP and independent department MCP adapters |
| `workers/agents/` | Agent workers (`BaseAgent.think()` in `base_agent.py`) |
| `decisions/` | ADRs — check before changing architecture |
| `bus/` | Queue, dispatch records, evidence, proposals |
| `docs/API-KEY-PROTECTION.md` | Secret-handling full guide |

## Culture (operational, not slogans)

- **SOP > Memory** — read the SOP instead of recalling.
- **Trust > Permission** — decide L1–L4 and report; escalate L5 only.
- **Dashboard > Report** — 3–5 lines + status color beats a long report.
- Good enough + deployed beats perfect + unborn.
