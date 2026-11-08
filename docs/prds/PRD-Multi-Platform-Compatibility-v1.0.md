# PRD: SoloCorp OS — Multi-Platform Compatibility v1.0

**Author:** โปรดัค (Product Head)
**Authorized by:** CEO หนุมาน
**Date:** 2026-07-06
**Status:** Approved

> **ขอบเขต:** PRD นี้กำหนดบริบท compatibility ของ agent clients ภายนอก ไม่ใช่ roadmap ของ SoloCorp App. การใช้ MCP แผนกแบบ standalone เป็น requirement ที่คงอยู่; target app และลำดับ MVP ปัจจุบันอยู่ใน [`PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md`](PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md).

---

## Problem Statement

SoloCorp OS has 18 active agent profiles, a central bus, governance tooling (xGov/govctl), and department pipelines. Historically, full functionality was available only on **OpenCode** (native) and **Hermes** (profiles deployed). Other platforms — Claude Code, Codex CLI, Grok Build, and an unresolved CLI ("r") — had partial or no integration.

Fragmentation means:
- A user on Claude Code cannot invoke `@architect-songsak` by mention
- Pipeline commands (`/pipeline`, `/handoff`, `/status`) are not portable
- Skills (`.opencode/skills/`) are invisible outside OpenCode
- Codex CLI export exists but has no validation CI or ongoing sync
- Grok Build needed a first-class pack (now: `AGENTS.md` + `.grok/`)

---

## Goals

| # | Goal |
|:--|:-----|
| G1 | Every platform can invoke any of the 16 department heads by name or mention |
| G2 | Pipeline commands work on every platform (syntax may differ) |
| G3 | Skills are defined once and documented clearly for cross-platform invocation |
| G4 | "r" CLI is identified, scoped, and integrated (or officially marked out-of-scope) |
| G5 | A compatibility matrix is maintained and accurate at all times |

## Non-Goals

- Feature parity for MCP tools — each platform has its own MCP constraints
- Real-time pipeline state sync across platforms
- Building a new CLI adapter layer
- Automating "r" integration before the platform is confirmed

---

## Platform Compatibility Matrix

| Feature | Claude Code | Codex CLI | OpenCode | Hermes | Grok Build | "r" |
|:--------|:-----------:|:---------:|:--------:|:------:|:----------:|:---:|
| Agent profiles exist | Partial | Yes | Yes | Yes | Yes | Unknown |
| Agent @mention syntax | No | No | Yes | No | No | Unknown |
| Pipeline commands | Partial | No | Yes | No | Yes (`.grok/skills`) | Unknown |
| Skills invocable | No | No | Partial | No | Yes | Unknown |
| Governance (govctl) | Via Bash | Via Bash | Via Bash | Via hook | Via Bash | Unknown |
| MCP tools | Yes | Partial | Yes | No | Yes (project `.grok/config.toml`) | Unknown |
| Multi-agent delegation | Yes | No | Yes | No | Partial (depth 1) | Unknown |
| Config file | CLAUDE.md | .codex/config.toml | opencode.json | ~/.hermes/profiles/ | AGENTS.md + `.grok/` | Unknown |
| Department agents spawnable | Partial | Export | Yes | Profiles | Yes (core Heads) | Unknown |

**Legend:** Yes = working, Partial = incomplete, No = not implemented, Unknown = TBD

---

## Current State by Platform

**OpenCode** — Gold standard. 20 agents, pipeline commands, MCP, skills. Gap: `.opencode/skills/` not linked to `skills/`.

**Hermes** — Profiles deployed. No pipeline commands, no skill system, no MCP. Agent conversations only.

**Claude Code** — `CLAUDE.md` routing table exists. Agent tool supports delegation. Gap: no `/pipeline` slash command registration.

**Codex CLI** — Export script exists. Gap: no CI sync, no skill support.

**Grok Build** — First-class pack (2026-07-18): root `AGENTS.md`, `.grok/agents/` (CEO, Orchestrator, Architect, Product, Engineering, QA), pipeline skills (`/pipeline`, `/handoff`, `/status`, `/audit`, `/deploy`, `/brain`, `/route`), personas, project MCP for stealth browser. See `docs/GROK-SUPPORT.md`. Gaps: no `@mention` UX; specialist depth limited to one subagent level; not all 55+ specialists packaged as agents yet.

**"r"** — Platform identity unconfirmed. Possibly Roo Code, Roo Cline, or other. Cannot scope until identified.

---

## Key Features Required

| Feature | Description |
|:--------|:------------|
| F1 Universal Invocation | All 16 heads invocable on every platform |
| F2 Pipeline Portability | `/pipeline`, `/status`, `/handoff`, `/deploy`, `/brain` on every platform |
| F3 Skill Discoverability | Single skills registry linked from all platform configs |
| F4 Codex Sync CI | Auto-run export script on profile changes |
| F5 "r" Identification | Engineering to confirm platform + compatibility scope |

---

## Success Metrics

| Metric | Target |
|:-------|:-------|
| Platform coverage | 4/5 platforms functional (r = TBD) |
| Agent invocation | All 16 heads invocable on Claude Code + Codex + OpenCode + Hermes |
| Pipeline commands | `/pipeline`, `/status`, `/deploy` on ≥3 platforms |
| Skill discoverability | `skills/REGISTRY.md` exists + linked in all configs |
| Codex drift | 0 agents out of sync after commit |

---

## Implementation Phases

### P0 — Fix Existing Gaps (Week 1)

| Task | Owner | Platform |
|:-----|:------|:---------|
| Link `skills/team-architect/` into `.opencode/skills/` | Engineering | OpenCode |
| Register pipeline commands as Claude Code slash commands | Engineering | Claude Code |
| Add CI step to run `export-codex-agents.py` on profile changes | Engineering | Codex CLI |
| Create `skills/REGISTRY.md` | Product | All |

### P1 — Expand + Identify (Weeks 2–3)

| Task | Owner | Platform |
|:-----|:------|:---------|
| Identify "r" platform | Engineering | "r" |
| Write Hermes pipeline command shim | Engineering | Hermes |
| Populate `.opencode/skills/` for all 13 departments | Product + Engineering | OpenCode |
| Write skill invocation docs for Claude Code + Codex | Product | Claude Code, Codex |

### P2 — Full Coverage + Validation (Weeks 4–5)

| Task | Owner | Platform |
|:-----|:------|:---------|
| Integrate "r" platform (if confirmed) | Engineering | "r" |
| Cross-platform smoke test suite | QA | All |
| Publish `docs/PLATFORM-COMPAT.md` | Product | — |
| govctl guard: block merge if matrix is stale | Engineering | All |
