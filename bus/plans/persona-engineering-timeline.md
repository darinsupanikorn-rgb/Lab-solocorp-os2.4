# Persona Engineering Upgrade — Timeline & Handoff Plan

**Source Plan:** `persona-engineering-upgrade-v1.md`
**Owner:** @orchestrator-wut (พี่วุฒิ)
**Timeline:** W1 = Jul 12–18, 2026
**Status:** ACTIVE

---

## 1. Work Package Timeline

| WP | Owner | Dept | Start | End | Gates |
|:---|:------|:-----|:------|:----|:------|
| **WP1** — 5-Layer Persona Template | @design-kreet | Design | W1 Mon | W1 Fri | G1 |
| **WP2** — Quality Gate Validation | @architect-songsak | Architect | W1 Mon | W2 Wed | G1, G2 |
| **WP3** — Smoke Test Pipeline | @qa | QA | W2 Thu | W2 Fri | G2, G3 |
| **WP4** — Evolution Brain System | @architect-songsak | Architect | W2 Mon | W3 Fri | G2, G4 |
| **WP5** — Data Collector Tools | @content-creator-sek | Content | W3 Mon | W3 Fri | G5 |
| **WP6** — Privacy Guard → Legal Vault | @legal-tulya | Legal | W3 Mon | W3 Fri | G5 |
| **WP7** — Compare Mode | @orchestrator-wut | Orchestrator | W4 Mon | W4 Fri | G6 |

---

## 2. Checkpoint Gates

| Gate | When | Criteria | Who Attends |
|:-----|:-----|:---------|:------------|
| **G1** | W1 Fri | WP1 complete — 18 profiles migrated to 5-Layer template + example | CEO, Design, Architect |
| **G2** | W2 Wed | WP2 complete — validate script passes on all 18 profiles, CI-ready | CEO, Architect, QA |
| **G3** | W2 Fri | WP3 complete — 3 smoke tests run against profiles, /deploy integration done | CEO, QA, Orchestrator |
| **G4** | W3 Fri | WP4 complete — version_manager.py live, rollback tested, brain/ updated | CEO, Architect |
| **G5** | W3 Fri | WP5 + WP6 complete — collector report + PII scan module delivered | CEO, Content, Legal |
| **G6** | W4 Fri | WP7 complete — compare mode spec + prototype shipped | CEO, Orchestrator |

---

## 3. Dependencies

```
WP1 ───────────────────────────────────────────────────────┐
  │                                                         │
  └──► WP2 ──► WP3 ──► all complete ──► WP7 (consumes all) │
  │       │      │                              │           │
  │       └──────┘                              │           │
  │                                             │           │
  └─────────────────────────────────────────────┘           │
                                                            │
WP4 ──► (standalone, but needs WP1 profile structure) ────┘
WP5 ──► standalone ───────────────────────────────────────┐
WP6 ──► standalone ───────────────────────────────────────┤
                                                            │
                    All WPs complete ───────────────────► WP7 (Compare Mode)
```

**Formal dependency table:**

| WP | Depends On | Reason |
|:---|:-----------|:-------|
| WP2 | WP1 | Validation schema must match new template structure |
| WP3 | WP1, WP2 | Smoke test questions need template fields + validation criteria |
| WP4 | WP1 | Evolution system appends to 5-Layer persona files |
| WP5 | — | Standalone tool review (no code dependency) |
| WP6 | — | Standalone privacy scanner port |
| WP7 | WP1, WP2, WP3, WP4, WP5, WP6 | Compare mode consumes all upgraded profiles + quality data |

---

## 4. Handoff Points

```
CEO (Vision)
  └──► [H0] Orchestrator ─── Timeline + delegation
         ├──► [H1] Design ─── WP1 brief: template spec, profile list
         │     └──► [H2] Architect ─── WP2: template output → validation schema
         │           └──► [H3] QA ─── WP3: validated profiles → smoke test questions
         ├──► [H4] Architect ─── WP4: evolution system + brain/ integration
         ├──► [H5] Content Creator ─── WP5: collector tool review brief
         ├──► [H6] Legal ─── WP6: privacy guard port brief
         └──► [H7] Orchestrator ─── WP7: compare mode (awaits all above)
```

### Handoff Record Template

Each handoff follows this protocol (defined in Orchestrator SOUL.md):

```
## Handoff — [From] → [To]

**Pipeline ID:** PERSONA-ENG-UPGRADE
**WP:** WP[N]
**From:** @handle
**To:** @handle
**Timestamp:** [datetime]

**Context:**
[Summary of prior work + decisions made]

**Deliverables Attached:**
- [file/link]

**Explicit Request:**
[Concrete deliverable + acceptance criteria]

**Known Issues:**
[Transparent blockers]

**Deadline:** [date]
```

### Detailed Handoff Schedule

| Ref | From | To | WP | When | Key Deliverable |
|:----|:-----|:---|:---|:-----|:----------------|
| H0 | CEO | Orchestrator | All | W0 | Approved plan + department assignments |
| H1 | Orchestrator | Design (Kreet) | WP1 | W1 Mon | Template brief: 5-Layer structure, 18 profiles to migrate |
| H2 | Design (Kreet) | Architect (Songsak) | → WP2 | W1 Fri | 18 migrated SOUL.md + template example |
| H3 | Architect (Songsak) | QA | → WP3 | W2 Wed | Validation script + pass/fail report for all 18 profiles |
| H4 | Orchestrator | Architect (Songsak) | WP4 | W2 Mon | Evolution brain spec + version_manager.py pattern ref |
| H5 | Orchestrator | Content Creator (Sek) | WP5 | W3 Mon | Tool review brief: slack/github/email collectors |
| H6 | Orchestrator | Legal (Tulya) | WP6 | W3 Mon | Privacy guard port brief + compliance pipeline spec |
| H7 | All WPs | Orchestrator (Wut) | WP7 | W4 Mon | All deliverables complete → compare mode design |

---

## 5. WP7: Compare Mode — Specification

**Owner:** @orchestrator-wut (พี่วุฒิ)
**Dept:** Orchestrator
**Depends on:** WP1 → WP6 complete
**Output:** `/compare` command spec + prototype

### 5.1 Concept

Port the `/compare` prompt concept from `teammate-skill/prompts/compare.md` to SoloCorp's Department Head context. Instead of comparing generic teammates, we compare **Department Heads** side-by-side to answer routing/handoff questions:

- "Who should handle this task?"
- "Which department is best suited for this goal?"
- "How would Songsak vs Kreet approach this problem?"
- "Should this pipeline route to Design or Product first?"

### 5.2 Comparison Inputs

For each Department Head, the compare mode reads:

| Data Source | Field | Purpose |
|:------------|:------|:--------|
| `profiles/NN-name/SOUL.md` | Layer 0 Core Rules | Hard constraints (what they will/won't do) |
| | Layer 1 Identity | Role, reports to, team size |
| | Layer 2 Communication | Catchphrases, speaking style |
| | Layer 3 Decision | Priority ranking, pushback pattern |
| | Model Spec | Model tier, capability domain |
| | Core Discipline | 5 pillars of their discipline |
| | KPI | Success metrics |
| `scripts/validate-soul-profiles.py` | Quality score | Validation pass/fail per criterion |
| `brain/version_manager.py` | Evolution history | Recent updates, expertise growth |
| Central Bus | Routing history | Past handoff patterns, SLA data |

### 5.3 Comparison Modes

#### Mode A: Quick Overview (no context)

Command: `/compare [dept-A] vs [dept-B]`

Output: Compact table with contrasting dimensions:

```
━━━ @architect-songsak vs @design-kreet ━━━

                     Architect (Songsak)         Design (Kreet)
Role:                Head of Architect           Creative Director
Model:               DeepSeek V4 Pro (Tier A)    GLM-5.2 (Tier B)
Priority:            Pipeline Integrity > Speed  Consistency > Novelty
Decision Style:      Systematic, rule-based      Intuitive, principle-based
Pushback:            "Show me the data"          "This violates design system"
Catchphrase:         "Simpler is better"         "Every pixel has a reason"
Domain:              Pipeline, Bus, Routing      Brand, Visual, UX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Mode B: Routing Decision

Command: `/compare [dept-A] vs [dept-B] for "[task description]"`

When the orchestrator needs to decide routing:

1. Parse task description for domain keywords
2. Match against each department's scope (Layer 1 + Core Discipline)
3. Simulate each Head's response (2-3 sentences in character)
4. Recommend routing with rationale

```
🤔 "Who should handle: 'Design a pipeline monitoring dashboard'?"

@architect-songsak would:
  "I'll route this through Pipeline Auditor — they own monitoring specs
   and health probes. Expected: dashboard mockup in 1 day."
  → Direct ownership, fast turnaround, within scope

@design-kreet would:
  "Happy to make it look beautiful, but I need UX requirements from
   the user first. Who's the audience? What decisions will they make?"
  → Would add design thinking but slower due to discovery phase

Recommendation: @architect-songsak for build, @design-kreet review for UX polish.
```

#### Mode C: Handoff Conflict Resolution

When two departments both claim (or reject) a task:

```
🎭 Conflict: "Both Engineering and Architect claim ownership of deployment pipeline."

@architect-songsak: "Pipeline design is my mandate — I own Central Bus.
                     Engineering implements what I route."
@engineering-changful: "I write the code that makes pipelines run.
                        Architect designs the theory, I build the practice."

Orchestrator resolution:
  → Architect: Design pipeline topology + routing rules
  → Engineering: Implement pipeline code + deploy
  → Handoff: Architect routes → Engineering builds → QA validates
```

### 5.4 Data Flow for Compare Mode

```
Input: /compare [A] vs [B] [optional: "for <task>"]

1. Load both profiles/SOUL.md
2. Extract comparison dimensions (Layer 0-3, Model, KPIs)
3. If task provided:
   a. Parse task domain keywords
   b. Score relevance per department scope
   c. Simulate response for each (in-character)
   d. Recommend routing
4. Render compact comparison table
5. Output to Central Bus as handoff advisory
```

### 5.5 Compare Mode Command Spec

```
/compare <dept-slug-a> vs <dept-slug-b> [for "<task description>"]
/compare all for "<task description>"           # compare all relevant depts
/compare <dept-a> <dept-b> <dept-c>             # 3-way comparison
```

### 5.6 Prototype Plan

| Step | What | Output |
|:-----|:-----|:-------|
| 1 | Read all 18 SOUL.md → extract comparison dimensions | `scripts/compare-dimensions.yaml` |
| 2 | Build `/compare` prompt template | `prompts/compare-prompts.md` |
| 3 | Implement comparison scoring for routing | `scripts/routing-compare.py` |
| 4 | Wire to `/deploy` as advisory step | `opencode.json` routing update |
| 5 | Test with 3 scenarios (clear, ambiguous, conflict) | Test report |

### 5.7 Acceptance Criteria

- `/compare A vs B` produces a compact table with ≥5 contrasting dimensions
- `/compare A vs B for "task"` produces a routing recommendation + rationale
- Response is in-character for both Department Heads
- Handles 3+ department comparison in table format
- Falls back gracefully if profile data is incomplete (marks missing fields)

---

## 6. Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|:-:|:-----|:-----------|:-------|:-----------|:------|
| R1 | WP1 template doesn't cover all 18 profiles | Medium | High | Design to produce template + migrate 2 pilot profiles first before bulk | @design-kreet |
| R2 | WP2 validation script blocks WIP profiles (false positives) | Medium | Medium | Allow per-profile overrides; manual review queue set up before W2 end | @architect-songsak |
| R3 | WP3 smoke tests fail on valid profiles (false negatives) | Medium | Medium | Tune prompts per department role; run in non-blocking mode first week | @qa |
| R4 | WP4 version merge conflicts with existing brain/ data | Low | High | Test merge on a fork of brain/ first; keep full backup before upgrade | @architect-songsak |
| R5 | WP5 collector scripts don't match SoloCorp workflow (e.g. no real Slack API) | Medium | Low | Scope down to supported sources only (GitHub PRs, local files); defer unsupported | @content-creator-sek |
| R6 | WP6 privacy scanner flags too many false positives | Medium | Medium | Tune regex rules for SoloCorp context; allow whitelist-based exemptions | @legal-tulya |
| R7 | WP7 compare mode has no data to compare (other WPs slip) | Low | Critical | WP7 start is W4 — acts as buffer; if earlier WPs slip, adjust WP7 scope to design-only | @orchestrator-wut |
| R8 | WPs overlap contention (Songsak owns WP2 + WP4 simultaneously) | High | Medium | WP4 design spec done in W1 (idle); WP2 coding W1-W2 → WP4 coding W2-W3 — sequential pipeline | @orchestrator-wut |
| R9 | Owner (Dr.solodev) unavailable for final sign-off | Low | High | CEO (หนุมาน) has delegated authority for all gates except G6 | CEO |

---

## 7. Escalation Path

```
Gate issues → Report to Orchestrator (พี่วุฒิ)
  ├── Resolvable at WP level → Orchestrator coordinates fix
  ├── Cross-department conflict → Orchestrator mediates + handoff table
  └── Blocking / scope change → Escalate to CEO (หนุมาน) with recommendation
```

---

## 8. Success Criteria

- All 7 WPs delivered within 4 weeks
- Every gate passes with sign-off from CEO
- No handoff requires >1 round of clarification
- WP7 compare mode correctly recommends routing for ≥3 test scenarios
- Risk register: ≤1 high-severity risk realized (and mitigated within 24h)
