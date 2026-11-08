# SoloCorp OS — Grok Platform Pack

Makes **Grok Build CLI** a first-class host for SoloCorp OS 2.4 (alongside OpenCode, Hermes, Codex).

**Parity status:** Phase 0 docs ✅ · Plan 1–3 ⏳ — full roadmap in [`docs/GROK-PARITY-PLAN.md`](../docs/GROK-PARITY-PLAN.md)

## Gap vs OpenCode (today)

| มิติ | OpenCode | Grok pack now | Target (Plan 1+) |
|:-----|:---------|:--------------|:-----------------|
| Agents | 21 in `.opencode/agents/` | **6** in `agents/` | ≥ 21 + `coo-kit` |
| Slash skills | 19 commands | **7** in `skills/` | 19 |
| MCP solocorp | 7 tools | 7 tools ✅ | + runtime (Plan 2) |
| Badge | 🟢 | 🟡 Partial | 🟢 after Plan 3 |

Do not start Plan 1 code until Owner says **เริ่ม Plan 1**. See parity plan for acceptance gates.

## What's included

| Path | Purpose |
|:-----|:--------|
| `../AGENTS.md` | Project rules injected every Grok session in this repo |
| `agents/` | Department Head agent definitions (spawnable subagent types) |
| `skills/` | Pipeline slash commands: `/pipeline`, `/handoff`, `/status`, … |
| `personas/` | Optional behavioral overlays for subagents |
| `config.toml` | Project-scoped MCP (`solocorp` + stealth browser) |
| `../docs/GROK-PARITY-PLAN.md` | **Plan 1 / 2 / 3** toward OpenCode gold |
| `../docs/GROK-SUPPORT.md` | Support guide + limits |

## Quick start

```bash
cd /path/to/Lab-solocorp-os2.4
source .venv/bin/activate
export PYTHONPATH=.
grok
```

Then try:

```
/status
/route อยากเพิ่ม endpoint health metrics บน central bus
/pipeline central-bus metrics endpoint
```

Or natural language:

- “ทำตัวเป็น CEO แล้วแตกงานไป Engineering + QA”
- “spawn architect-songsak ไป review central_bus routing”
- “รัน bus แล้วเช็ค /v1/health”

## Agent types (spawnable)

| `subagent_type` | Role |
|:----------------|:-----|
| `ceo-hanuman` | CEO — strategy, prioritization, final call |
| `orchestrator-wut` | Multi-dept pipeline coordination |
| `architect-songsak` | Central Bus, routing, monitoring |
| `product-produck` | PRD / roadmap / acceptance |
| `engineering-changful` | Implementation (code) |
| `qa` | Tests, quality evidence |

Parent may also use built-in `explore` / `plan` / `general-purpose`.

## Skills (slash commands)

| Command | What it does |
|:--------|:-------------|
| `/pipeline <feature>` | Full cycle: route → plan → implement → QA → status |
| `/handoff <from> <to> <task>` | Structured handoff record |
| `/status` | Bus + gov + queue health snapshot |
| `/audit [scope]` | Audit trail / governance check |
| `/deploy` | Export profiles / validate packaging |
| `/brain <context>` | Persist session notes under `bus/projects/` |
| `/route <request>` | Map request → department + recommended agent |

## Runtime services

| Service | Start | Check |
|:--------|:------|:------|
| Central Bus | `uvicorn central_bus.main:app --host 127.0.0.1 --port 8099` | `curl -s localhost:8099/v1/health` |
| govctl API | `python -m govctl_cli api start` | `curl -s localhost:8765/api/v1/health` |

Always set `PYTHONPATH=.` from repo root (or use activated `.venv` with editable install).

## MCP

Project `.grok/config.toml` wires:

| Server | Purpose |
|:-------|:--------|
| **solocorp** | Departments, SOUL profiles, route request, commands (needs `.venv` + `PYTHONPATH`) |
| **stealth_browser** | Browser automation (optional) |

```bash
grok mcp list   # expect: solocorp + stealth_browser (project)
```

Disable either with `enabled = false` in `.grok/config.toml` if unused.

Runtime services (bus + govctl + worker):

```bash
bash scripts/start-services.sh
```

## Compatibility limits (honest)

| Works well | Partial / not native |
|:-----------|:---------------------|
| Dev runtime (bus, govctl, tests) | OpenCode-only `@mention` UI |
| Department agents via spawn (6 Heads) | Full 21+ Heads (Plan 1) · 55+ specialists |
| Pipeline skills (7) | Full 19 OpenCode commands (Plan 1) |
| CLAUDE.md + AGENTS.md routing | Infinite multi-agent depth (Grok max depth 1 → Plan 2 fan-out) |

**Roadmap:** [`docs/GROK-PARITY-PLAN.md`](../docs/GROK-PARITY-PLAN.md) · Guide: [`docs/GROK-SUPPORT.md`](../docs/GROK-SUPPORT.md) · Matrix: [`docs/PLATFORM-COMPAT.md`](../docs/PLATFORM-COMPAT.md)

## Verify pack is loaded

```bash
cd /path/to/Lab-solocorp-os2.4
grok inspect
```

Confirm `AGENTS.md`, project skills, and agents appear. In TUI: type `/` and look for `/pipeline`, `/status`, etc. Open `/config-agents` to see project agents.
