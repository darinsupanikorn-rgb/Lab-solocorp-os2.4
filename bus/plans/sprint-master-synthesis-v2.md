# 🏃 Sprint 2: Master Synthesis — Integration

**Owner:** CEO หนุมาน  
**Start:** 2026-07-27  
**Duration:** 2 สัปดาห์ (Sprint 2-3 จาก Master Synthesis timeline)  
**Status:** ACTIVE  
**Execution Mode:** Hybrid — CEO direct + COO dispatch + Department Heads

---

## Context

Sprint 1 (Clear Overdue) dispatched 7 tasks + 1 WP. Evidence shows **LLM timeout** in agent worker pipeline — agents received tasks but couldn't produce deep results via `opencode run --pure`. 

**Sprint 2 approach:**
- CEO (ผม) execute high-value cognitive work directly in-session
- COO (Kit) handles routing, triage, monitoring
- Department Heads receive clear briefs for async execution
- Evidence collected manually per deliverable

---

## Sprint 2 — Tracks

### 🔴 Track A: SkillHub — First Skill Publish (Priority)

Objective: Ship first `@solocorp/*` skill to SkillHub to validate the pipeline.

| # | Task | Executor | Deliverable | Target |
|:-:|:-----|:---------|:------------|:-------|
| A1 | Define `@solocorp/ceo/sprint-plan` skill schema | CEO (direct) | JSON schema + README | Day 1 |
| A2 | Register with SkillHub API | CEO (direct) | API call → package published | Day 1 |
| A3 | Verify → skill discoverable | CEO (direct) | Screenshot/curl output | Day 1 |

### 🟡 Track B: COO Operational Takeover

Objective: Kit runs first independent dispatch cycle.

| # | Task | Executor | Deliverable | Target |
|:-:|:-----|:---------|:------------|:-------|
| B1 | Generate daily ops status from Central Bus | COO dispatch agent | Status report | Day 1 |
| B2 | Route 3 L1-L2 requests to correct departments | COO dispatch agent | Dispatch records | Day 2 |
| B3 | SOP compliance scan | SOP checker | Full report | Day 3 |
| B4 | Proposals from department heads | Proposal system | ≥2 proposals | Week 2 |

### 🟢 Track C: Master Synthesis Continuation

Continue remaining Master Synthesis tasks with clear briefs.

| # | Task | Dept | Owner | Deliverable | Target |
|:-:|:-----|:-----|:------|:------------|:-------|
| C1 | RD-02: Deep Ideation — concept network | R&D Lab | Lead Researcher | Network map + 5 research ideas | Week 1 |
| C2 | AR-04: Publish curated Antigravity skills | Architect | SkillHub Admin | 10 skills published | Week 1 |
| C3 | CS-02: Red Team Campaign #1 design | Cyber Security | Red Team Operator | Campaign plan + scope | Week 1 |
| C4 | EN-03: Dev Environment Standard | Engineering | Senior Dev | Docker + devcontainer spec | Week 2 |
| C5 | DS-01: SOUL.md v2 apply to 5 depts pilot | Design | Design Team | 5 depts migrated | Week 2 |
| C6 | QA-01: Test SkillHub deployment | QA | QA Team | Smoke test report | Week 2 |

### 🔵 Track D: Proposals Review (CEO)

| # | Title | Dept | Status | Action |
|:-:|:------|:-----|:-------|:-------|
| PROP-0001 | Migrate CI/CD → GitHub Actions | Engineering | DEFERRED | รอ COO review feasibility |
| PROP-0002 | Design System v2 — Dark Mode + A11y | Design | DEFERRED | รอ DS-01 template settle |
| PROP-0004 | User Onboarding Flow Redesign | Product | DEFERRED | รอ COO + Product sync |

---

## Execution Plan

### Session Today (2026-07-27)

| Step | Action | Who |
|:----:|:-------|:----|
| 1 | ✅ Build Sprint 2 plan | CEO |
| 2 | 🔲 Dispatch A1-A3 → SkillHub first skill | CEO direct |
| 3 | 🔲 Dispatch B1 → COO daily ops report | CEO → COO |
| 4 | 🔲 Dispatch C1-C6 → Department briefs | CEO → Central Bus |
| 5 | 🔲 Commit + push sprint plan + dispatches | CEO |

---

## Success Criteria

- ✅ SkillHub has ≥1 `@solocorp/*` package published
- ✅ COO produces first daily ops report
- ✅ Master Synthesis tasks progressing (evidence per task)
- ✅ 2+ department proposals submitted to COO
- ✅ Git clean at end of Sprint 2

---

*SoloCorp OS — System First, Everything Follows*
