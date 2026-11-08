# SoloCorp OS × Grok Build — Support Guide

**Status:** Active (v1 pack) · **Parity:** Planned (Phase 0 docs done)  
**Updated:** 2026-07-27  
**Pack location:** `.grok/` + root `AGENTS.md`  
**Parity plan:** [`docs/GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md) — Plan 1 → 2 → 3 ไปสู่ OpenCode gold

---

## Goal

Let Grok CLI develop and operate SoloCorp OS without requiring OpenCode for everyday runtime/dev work, while remaining honest about gaps vs full multi-agent org UX.

**Roadmap:** ปิด gap กับ OpenCode ตาม [`GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md)  
- Phase 0 (docs) ✅ · Plan 1 (agents+skills) ⏳ · Plan 2 (MCP/runtime) ⏳ · Plan 3 (smoke/CI 🟢) ⏳

---

## What works

| Capability | How |
|:-----------|:----|
| Project rules | `AGENTS.md` auto-loaded in repo |
| Pipeline commands | `/pipeline` `/handoff` `/status` `/audit` `/deploy` `/brain` `/route` (7/19 vs OpenCode) |
| Department agents | `.grok/agents/*` — **6** spawnable Heads (target ≥21 + COO ใน Plan 1) |
| Personas | `.grok/personas/*.toml` |
| Runtime | Central Bus, govctl, loop_runner, scoped pytest |
| MCP | `solocorp` + `stealth_browser` via `.grok/config.toml` |

---

## Quick test checklist

Run from repo root:

```bash
source .venv/bin/activate
export PYTHONPATH=.
grok
```

In TUI:

1. Type `/` → confirm SoloCorp skills appear (`pipeline`, `status`, …).
2. Run `/status` → health table (bus may be down; that is OK).
3. Run `/route เพิ่ม metrics endpoint บน central bus` → Engineering + Architect.
4. Run `/pipeline smoke status check` → plan without needing all services up.
5. Ask: “spawn architect-songsak ไล่ central_bus router” → subagent uses project agent.
6. `grok inspect` (shell) → shows `AGENTS.md` and project skills/agents.

Optional live runtime (recommended one-shot):

```bash
bash scripts/start-services.sh
# starts Central Bus :8099 + govctl API :8765 + agent worker (idempotent)
curl -s http://127.0.0.1:8099/v1/health
curl -s http://127.0.0.1:8765/api/v1/health
```

Then `/status` again should show bus **up**.

**MCP (project `.grok/config.toml`):** `solocorp` + `stealth_browser`.  
Confirm with `grok mcp list` — `solocorp` must show as project-scoped.

---

## Compatibility matrix (Grok column)

| Feature | Grok |
|:--------|:----:|
| Agent profiles on disk | Yes |
| Department agents invocable | Yes (spawn / role-play) |
| OpenCode-style `@mention` | No |
| Pipeline slash commands | Yes (skills) |
| Skills discoverable | Yes (`.grok/skills`) |
| Governance (govctl) | Yes (via shell) |
| MCP tools | Yes (project config) |
| Multi-agent delegation | Partial (depth 1) |
| Config entry | `AGENTS.md` + `.grok/` |

Full matrix: `docs/prds/PRD-Multi-Platform-Compatibility-v1.0.md`

---

## Limits

1. **Subagent depth = 1** — Orchestrator parent must fan-out; children cannot spawn. (Plan 2 compensates)
2. **Not a drop-in OpenCode** — no native `@ceo-hanuman` mention UI. (Plan 3: mention shim table)
3. **55+ specialists** — only core Heads packaged as Grok agents in v1; rest via `profiles/*/SOUL.md` role-play.
4. **Command/agent surface** — 7 skills / 6 agents today vs OpenCode 19 / 21 — see parity plan.
5. **MCP path** — stealth browser command uses absolute paths for this machine; adjust `.grok/config.toml` if the repo moves.
6. **pytest** — always scope paths; do not collect entire monorepo.

---

## Parity roadmap (short)

| Phase | What | Status |
|:------|:-----|:------:|
| **0** | Docs: this guide + `GROK-PARITY-PLAN.md` | ✅ |
| **1** | Agents ≥21 + skills 19 (OpenCode surface) | ⏳ |
| **2** | MCP runtime ops + export sync + fan-out | ⏳ |
| **3** | Smoke/CI + matrix 🟢 Active | ⏳ |

Full tasks, acceptance, metrics: **[`docs/GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md)**

---

## Extending the pack

| Add | Where |
|:----|:------|
| New slash workflow | `.grok/skills/<name>/SKILL.md` |
| New department agent | `.grok/agents/<name>.md` |
| Behavioral overlay | `.grok/personas/<name>.toml` |
| MCP server | `.grok/config.toml` `[mcp_servers.*]` |

Keep parity plan + this doc in sync when adding skills/agents. Prefer Plan 1 standards (frontmatter) in the parity plan.

---

## Related

- [`docs/GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md) — **OpenCode parity Plan 1–2–3**
- `.grok/README.md` — pack overview  
- `AGENTS.md` — session rules  
- `CLAUDE.md` — Claude/OpenCode routing (still valid)  
- `docs/PLATFORM-COMPAT.md` — cross-platform matrix  
- `docs/operations-runbook.md` — govctl ops  
 
