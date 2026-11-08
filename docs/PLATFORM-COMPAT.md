# 📱 Platform Compatibility

> SoloCorp OS รองรับ AI Client ไหนบ้าง? — 2026-07-27

## Overview

| Platform | Config Path | Skills | Agents | Status |
|:---------|:------------|:------:|:------:|:------:|
| **OpenCode** | `opencode.json` | ✅ 18 commands | ✅ 4 agents | 🟢 Active |
| **Claude Code** | `.claude/settings.json` | ✅ 6 commands | ❌ (via MCP) | 🟡 Partial |
| **Grok Build** | `.grok/agents/` + `.grok/skills/` | ✅ 7 pipeline (→19 Plan 1) | ✅ 6 Heads (→≥21 Plan 1) | 🟡 Partial · [parity plan](GROK-PARITY-PLAN.md) |
| **Codex CLI** | `.codex/config.toml` + `.codex/agents/` | ❌ | ✅ 86 agents | 🟡 Partial |
| **Hermes** | `dist/hermes/` profiles | ❌ | ✅ 81 profiles | 🟡 Partial |
| **Cursor** | `.cursor/mcp.json` | ❌ | ❌ (via MCP) | 🟢 MCP only |

---

## OpenCode (Primary)

**Config**: `opencode.json`

| Feature | Status | Notes |
|:--------|:------:|:------|
| CEO default agent | ✅ | `default_agent: ceo-hanuman` |
| 18 slash commands | ✅ | pipeline, handoff, status, audit, deploy, brain, pipeline-bridge, mirror-check, bootstrap, triage, mirror, orchestrate, summary, sprint-plan, daily-ops, eng-deploy, budget-check, smoke-test, rfc-new |
| Skills paths | ✅ | 7 paths in `skills.paths` incl. `@solocorp/` |
| MCP servers | ✅ | solocorp, github, stealth-browser |
| Profile references | ✅ | 9 reference paths (profiles, docs, decisions, etc.) |
| Auto-bootstrap | ✅ | `/bootstrap` on session start |

## Claude Code

**Config**: `.claude/settings.json`

| Feature | Status | Notes |
|:--------|:------:|:------|
| MCP servers | ✅ | solocorp + stealth-browser |
| Slash commands | ✅ | 6 commands registered |
| `.claude/commands/` | ✅ | 6 `.md` files (sprint-plan, daily-ops, eng-deploy, budget-check, smoke-test, rfc-new) |
| Agent model | ❌ | No native agent system — uses MCP for SoloCorp |
| Claude Code quick start | ❌ | No CLAUDE.md or QUICKSTART.md for Claude Code |

## Grok Build

**Config**: `.grok/skills/` + `.grok/agents/` + `AGENTS.md` + `.grok/config.toml`  
**Parity roadmap**: [`docs/GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md) (Phase 0 ✅ · Plan 1–3 ⏳) · Guide: [`GROK-SUPPORT.md`](GROK-SUPPORT.md)

| Feature | Status | Notes |
|:--------|:------:|:------|
| Pipeline skills | ✅ partial | 7 skills today; **19** target in Plan 1 (match `opencode.json`) |
| Department agents | ✅ partial | 6 spawnable Heads; **≥21 + coo-kit** in Plan 1 |
| Department skills | 🟡 | SkillHub `@solocorp/*` via bus; port as Grok skills in Plan 1–2 |
| MCP | ✅ | `solocorp` + `stealth_browser`; runtime tools (health/queue) in Plan 2 |
| Runtime | ✅ | `bash scripts/start-services.sh` → bus :8099 + govctl :8765 + agent worker |
| OpenCode gold badge | 🟡 | 🟢 only after Plan 3 acceptance (smoke + CI + demo) |

Quick start: `source .venv/bin/activate && export PYTHONPATH=. && bash scripts/start-services.sh && grok`

## Codex CLI

**Config**: `.codex/config.toml` + `.codex/agents/`

| Feature | Status | Notes |
|:--------|:------:|:------|
| Agent configs | ✅ | 86 agent TOML files |
| Export pipeline | ✅ | `scripts/export-codex-agents.py` — build + validate |
| Slash commands | ❌ | No commands section in `.codex/config.toml` |
| MCP | ❌ | Not yet configured |

## Hermes

**Config**: `dist/hermes/` (81 profiles)

| Feature | Status | Notes |
|:--------|:------:|:------|
| Profiles built | ✅ | `scripts/build-profiles.py` → 3 formats (droid/codex/hermes) |
| Hermes deploy | ❌ | Profiles built but not deployed to Hermes runtime |
| Agent commands | ❌ | No command system in Hermes |

## Cursor

**Config**: `.cursor/mcp.json`

| Feature | Status | Notes |
|:--------|:------:|:------|
| MCP servers | ✅ | solocorp + github |
| Slash commands | ❌ | Cursor uses OpenCode format via `opencode.json` |
| Agent integration | ❌ | Via MCP only |

---

## SkillHub Coverage by Platform

| Skill | OpenCode | Claude Code | Grok | Bus API |
|:-----|:--------:|:-----------:|:----:|:-------:|
| `/pipeline` | ✅ | ❌ | ✅ | ❌ |
| `/handoff` | ✅ | ❌ | ✅ | ❌ |
| `/status` | ✅ | ❌ | ✅ | ❌ |
| `/deploy` | ✅ (profile) | ❌ | ✅ | ❌ |
| `/brain` | ✅ | ❌ | ✅ | ❌ |
| `/pipeline-bridge` | ✅ | ❌ | ❌ | ✅ |
| `/mirror-check` | ✅ | ❌ | ❌ | ✅ |
| `/sprint-plan` | ✅ | ✅ | ❌ | ✅ |
| `/daily-ops` | ✅ | ✅ | ❌ | ✅ |
| `/eng-deploy` | ✅ | ✅ | ❌ | ✅ |
| `/budget-check` | ✅ | ✅ | ❌ | ✅ |
| `/smoke-test` | ✅ | ✅ | ❌ | ✅ |
| `/rfc-new` | ✅ | ✅ | ❌ | ✅ |

**Legend**: ✅ available | ❌ not yet ported | 🟡 partial

---

## Gaps & Next

| Gap | Priority | Resolution |
|:----|:--------:|:-----------|
| **Grok ↔ OpenCode parity** | **P1** | [`GROK-PARITY-PLAN.md`](GROK-PARITY-PLAN.md) — Plan 1 agents+skills, Plan 2 MCP, Plan 3 🟢 |
| Claude Code agent model | P3 | Create `.claude/CLAUDERC.md` for auto-agent |
| Grok dept skills | P1 | Covered by parity Plan 1–2 (port `@solocorp/*` + missing slash cmds) |
| Codex CLI commands | P3 | Add commands to `.codex/config.toml` |
| Hermes deployment | P3 | Add Hermes deploy step to `/deploy` pipeline |
| Cross-platform test suite | P2 | Create smoke test for each platform (Grok smoke = Plan 3) |
| All platform docs | P3 | Quickstart per platform |

---

*SoloCorp OS — System First, Everything Follows*
