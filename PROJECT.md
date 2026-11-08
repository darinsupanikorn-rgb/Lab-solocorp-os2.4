# SoloCorp OS 2.4 — Getting Started Guide

> **Status note (2026-11-02):** This is a legacy orientation guide; its readiness labels are historical and do not describe the Local-First App MVP. Current product status is in [the current PRD](docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md).

> A complete orientation for newcomers. Read this first to understand the
> entire system, its structure, and how to start using it effectively.

---

## What is SoloCorp OS?

SoloCorp OS is an **organizational operating system for AI agents**. It
transforms a single AI into a structured, multi-department company of
specialized agents — each with a dedicated Head, defined responsibilities,
and a clear chain of command.

The core insight: instead of asking one AI to do everything (which means
nobody is responsible for anything), SoloCorp OS divides work into 15
departments, each led by a Department Head who owns outcomes. Department
Heads delegate execution to specialist sub-agents and communicate with
other departments through structured handoffs.

Key metrics at a glance:

| Dimension | Value |
|:----------|:------|
| Departments | 18 (C-Level + System + Product + Revenue + Legal + Web3 + Content + NetEng + CyberSec + Psychology) |
| Department Heads | 18 |
| Specialist Agents | 55+ (across 18 departments) |
| Skills Integration | 93 skills |
| Pipeline Commands | 6 |
| Platforms | Hermes, OpenCode, Codex CLI, Grok Build |
| Runtime | Loop Runner (cron every 30 min) |
| Central Bus | Legacy guide's readiness claim (FastAPI v0.6, port 8099) |
| Status | Historical platform status; Local-First App MVP is in Phase 1 |

---

## Core Philosophy

SoloCorp OS is built on three non-negotiable pillars:

**1. Department Heads Do Not Work Themselves**

The Head's job is to lead — set direction, make decisions, resolve
blockers, and escalate when necessary. Execution belongs to specialist
sub-agents. If a Head is writing code or designing UIs, the system is
broken.

**2. Leadership & Management Skills**

Every Department Head must be skilled in delegation, team management,
cross-department communication, and strategic thinking. Technical
expertise is table stakes; leadership is the differentiator.

**3. Ownership Mindset**

Every Head is the owner of their department, not an employee. They own
outcomes, quality, and continuous improvement. There is no "not my job"
in SoloCorp OS.

---

## Why This Architecture?

The problem with most AI agent systems is they suffer from a single point
of failure — one orchestrator that must route everything, remember
everything, and execute everything. This creates:

- **Bottlenecks** — Every request waits for the orchestrator
- **Context loss** — One agent cannot hold context for all domains
- **No accountability** — When everything is everyone's job, nothing gets owned

SoloCorp OS solves this with:

| Problem | Solution |
|:--------|:---------|
| Single orchestrator bottleneck | Head-to-Head handoff — 80% of cases go direct |
| No domain expertise | 15 specialized departments with deep knowledge |
| Context loss | Each Head owns their domain context |
| Orphan work | Every task has an owner at every step |
| Slow execution | Data Layer bypasses Heads entirely |

---

## Hierarchy Structure

The chain of command flows from Human through CEO to C-Level, then to
Department Heads, and finally to Specialist Teams:

```
Dr.solodev (Human / Owner)
  └── CEO — เทอโบ (Turbo Chaisriram)
       │    Vision, Strategy, Final Decision
       │
       ├── CFO — meetoo                    Finance, Budget, Investment
       ├── CMO — มาร์ค                      Marketing, Content, Brand
       └── Orchestrator — พี่วุฒิ (Wut)     System Pipeline Coordination
            │
            └── Department Heads (05-18)
                 ├── 05-Architect     — พี่ทรงศักดิ์   — Central Bus
                 ├── 06-Product       — โปรดัค        — Roadmap / PRD
                 ├── 07-Engineering   — ช่างฟูล        — Code / Architecture
                 ├── 08-Design        — ครีเอท         — UX / Brand Visual
                 ├── 09-UI Designer   — UI Designer    — Interface
                 ├── 10-QA            — QA-ทีม         — Testing / Quality
                 ├── 11-Sales         — เซลส์          — B2B Pipeline
                 ├── 12-Support       — ซัพพอร์ต       — Customer Success
                 ├── 13-Legal         — ตุลย์           — Compliance / Law
                 ├── 14-Web3          — อัยวา          — Blockchain / DeFi
                 ├── 15-Content       — เสก            — Content / Creative
                 ├── 16-NetEng        — นีต            — Network / Infrastructure
                 ├── 17-CyberSec      — ซาย            — Security / Threat / IR
                 └── 18-Psychology    — จิต            — Behavior / Econ / Org
```

Communication rules:

- Human speaks only to CEO
- CEO commands C-Level (CFO, CMO, Orchestrator)
- Orchestrator coordinates Department Heads
- Department Heads speak to each other directly (Head-to-Head)
- Heads delegate execution to specialist sub-agents
- Sub-agents NEVER communicate with other departments directly

---

## Two-Tier Architecture

The system separates information flow into two distinct layers:

**Control Layer (Head-to-Head)**

This is the visible management layer. Department Heads communicate
status updates, approvals, exceptions, and handoffs. This layer is
deliberately lightweight — only what's needed for coordination.

```
  Head A ──(status/report)──→ Head B
    ↑                            ↑
    │  Minimal, structured       │
    │  communication only        │
```

**Data Layer (Autonomous via Central Bus)**

This is where actual work happens. Specialist agents write code, produce
designs, generate reports, and create documents — all flowing through the
Central Bus automatically. Heads never need to pass files around; they
simply see "Work Item X completed."

```
  Specialist A ──(write)──→ CENTRAL BUS ──(notify)──→ Specialist B
```

**Why this matters:**

| Aspect | Without Two-Tier | With Two-Tier |
|:-------|:-----------------|:--------------|
| Speed | Blocked by Head availability | Work flows autonomously |
| Scalability | Heads become bottlenecks | Heads stay strategic |
| Audit | Manual tracking | Central Bus logs everything |
| Resilience | Head failure stops work | Sub-agents continue executing |

---

## Department Responsibilities

| # | Department | Head | Core Function | Team Size |
|:-:|:-----------|:-----|:--------------|:---------:|
| 01 | CEO | เทอโบ | Vision, Strategy, Final Decision | 0 |
| 02 | CFO | meetoo | Finance, Budget, Investment | 3 |
| 03 | CMO | มาร์ค | Marketing, Content, Brand | 3 |
| 04 | Orchestrator | พี่วุฒิ | Cross-Dept Pipeline Coordination | 3 |
| 05 | Architect | พี่ทรงศักดิ์ | Central Bus, Routing, Monitoring | 5 |
| 06 | Product | โปรดัค | Feature Roadmap, PRD, Delivery | 3 |
| 07 | Engineering | ช่างฟูล | Backend, Frontend, Architecture | 3 |
| 08 | Design | ครีเอท | UX Research, Brand Visual | 3 |
| 09 | UI Designer | UI Designer | Interface, Component Library | 3 |
| 10 | QA | QA-ทีม | Testing, Quality, Evidence | 3 |
| 11 | Sales | เซลส์ | B2B Deal Strategy, Pipeline | 3 |
| 12 | Support | ซัพพอร์ต | Customer Success, Analytics | 3 |
| 13 | Legal | ตุลย์ | Compliance, Contracts, Law | 3 |
| 14 | Web3 | อัยวา | Blockchain, DeFi, Solana | 4 |
| 15 | Content Creator | เสก | Content, Creative, Media | 10 refs |
| 16 | Network Engineer | นีต | Network, Infrastructure, VPN, CDN, DNS | 3 |
| 17 | Cyber Security | ซาย | Threat Detection, Vulnerability, Incident Response | 3 |
| 18 | Psychology | จิต | User Behavior, Behavioral Economics, Org Psychology | 3 |

Each department has between 3-5 specialist agents who execute the
actual work. Department Heads do not execute — they lead, prioritize,
and make decisions.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Access to Hermes Agent Gateway (or OpenCode CLI)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Dr-SoloDev/Lab-solocorp-os2.4.git
cd Lab-solocorp-os2.4
```

### Step 2: Choose Your Interface

**Option A: OpenCode (Recommended)**

OpenCode is the primary CLI interface for SoloCorp OS. The `opencode.json`
configuration includes all 20 agents (15 department heads + 5 architect
specialists) and 6 pipeline commands.

```bash
opencode
```

Default agent is the CEO (หนุมาน). Speak naturally and the CEO will route
you to the correct department. Or use @mention to go direct:

```bash
opencode "@architect-songsak design a pipeline for the billing feature"
opencode "@changful implement user registration API endpoint"
opencode "@cfo-meetoo วิเคราะห์ผลประกอบการ Q3"
opencode "@product-produck review the new feature PRD"
```

**Option B: Codex CLI**

Export all profiles as Codex CLI sub-agents:

```bash
python3 scripts/export-codex-agents.py
codex
```

**Option C: Hermes Gateway**

All 15 profiles are deployed to Hermes Gateway and ready for use through
Hermes profiles system at `~/.hermes/profiles/<NN-name>/`.

### Step 3: Run a Pipeline Command

```bash
opencode "/pipeline billing-system-v2"
opencode "/status"
opencode "/audit pipeline"
```

### Step 4: Explore the Codebase

Start with these key files:

| File | Why Read It |
|:-----|:------------|
| `ARCHITECTURE.md` | System design, principles, and data flow |
| `profiles/INDEX.md` | Complete index of all agents and their status |
| `profiles/01-ceo/SOUL.md` | CEO profile — see how a Head operates |
| `profiles/05-architect/` | Most complete department with 5 sub-agents |
| `opencode.json` | Full OpenCode configuration |

---

## Repository Map

```
Lab-solocorp-os2.4/
│
├── opencode.json                  OpenCode full configuration (20 agents)
│
├── .opencode/
│   ├── agents/                    20 agent definitions (15 heads + 5 architects)
│   ├── commands/                  Pipeline workflow commands
│   └── skills/                    93 skills (symlinked from Hermes)
│
├── .claude/                       Claude Code configuration
├── .codex/                        Codex CLI sub-agents (60 TOML files)
│
├── profiles/
│   ├── INDEX.md                   Master index — start here
│   ├── 01-ceo/                    CEO — เทอโบ
│   ├── 02-cfo/                    CFO — meetoo
│   │   ├── meetoo/
│   │   │   └── team/              dana, riley, morgan
│   ├── 03-cmo/                    CMO — มาร์ค
│   ├── 04-orchestrator/           Orchestrator — พี่วุฒิ
│   ├── 05-architect/              Architect — พี่ทรงศักดิ์
│   │   ├── phee-thongsak/
│   │   │   └── team/              5 pipeline agents
│   ├── 06-product/                Product — โปรดัค
│   │   ├── produck/
│   │   │   └── team/              3 product specialists
│   ├── 07-engineering/            Engineering — ช่างฟูล
│   ├── 08-design/                 Design — ครีเอท
│   ├── 09-ui-designer/            UI Designer
│   ├── 10-qa/                     QA — QA-ทีม
│   ├── 11-sales/                  Sales — เซลส์
│   ├── 12-support/                Support — ซัพพอร์ต
│   ├── 13-legal/                  Legal — ตุลย์
│   ├── 14-web3/                   Web3 — อัยวา
│   ├── 15-content-creator/        Content Creator — เสก
│   └── default/                   Fallback profile
│
├── loop_runner/                   Auto-pilot cron system
│   ├── main.py                    Cron entry point (every 30 min)
│   ├── runner.py                  Base Loop class
│   ├── state.py                   SQLite persistent state
│   └── loops/
│       ├── daily_brief.py         CEO morning report (L1)
│       ├── subscription_audit.py  CFO subscription scan (L4)
│       └── brain_auto_commit.py   Auto-commit brain files (L4)
│
├── scripts/                       Utility scripts
│   ├── build-profiles.py          Build/validate Hermes profiles
│   ├── export-codex-agents.py     Export Codex CLI sub-agents
│   └── pipeline_until_score.py    Pipeline scoring utility
│
├── central_bus/                   Central Bus — legacy guide status; see current release audit
│   ├── main.py                    FastAPI daemon (busd) — port 8099, 5 endpoints
│   ├── queue.py                   Async queue (SQLite WAL + JSONL dual backend)
│   ├── router.py                  Message routing (keyword + TF-IDF + SQLite rules)
│   ├── audit.py                   Audit logger (SQLite-backed)
│   ├── db.py                      Database manager (SQLite WAL)
│   ├── state.py                   State management
│   ├── monitor_watchdog.py        Health monitor (PARTIAL — JSONL backend)
│   ├── dashboard.py               Project-state dashboard (PARTIAL — no HTTP endpoint)
│   ├── guard_runner.py            xGov guard gate runner
│   ├── webhook_receiver.py        Inbound webhook handler
│   ├── api_compliance.py          Compliance validator router
│   ├── aar.py                     After Action Review generator
│   ├── facts.py                   Context facts service
│   ├── semantic.py                TF-IDF semantic router
│   ├── config.py                  Settings (host, port, paths)
│   ├── models.py                  Pydantic message models
│   ├── migrate.py                 DB migration runner
│   ├── open_design.py             Open Design read-only bridge
│   ├── bus.db                     SQLite WAL database (live)
│   └── requirements.txt           Python dependencies
│
├── bus/                           Central Bus runtime data
│   ├── queue/                     JSONL queue files (high/normal priority + dead_letter/)
│   ├── projects/                  Active project state dirs
│   ├── governance/                Governance state dirs
│   └── system/                   routing_rules.json, semantic_profiles.json
│
├── decisions/                     Architecture Decision Records (ADRs)
├── tests/                         Phase test suites (1-4)
│
├── ARCHITECTURE.md                System architecture overview
├── README.md                      Project landing page
├── PROJECT.md                     This file — getting started guide
├── CHANGELOG.md                   Version history
└── LICENSE                        Proprietary license
```

---

## How Work Flows Through the System

Understanding the end-to-end flow helps make sense of why the system
is structured the way it is:

```
  PHASE 1: Intake
  ───────────────
  Human ──→ CEO ──→ Understand request ──→ Route to correct department

  PHASE 2: Planning
  ─────────────────
  Department Head receives brief
    → Delegates to specialist sub-agent(s)
    → Sub-agent researches, plans, and proposes

  PHASE 3: Execution
  ──────────────────
  Sub-agent executes the work
    → Output written to Central Bus
    → Head notified only on completion
    → If blocked → escalate to Head

  PHASE 4: Handoff (if cross-department)
  ─────────────────────────────────────
  Head A sends structured handoff to Head B
    → Pipeline Auditor logs the handoff
    → Head B receives and delegates to their team

  PHASE 5: Delivery
  ─────────────────
  Work completed → Central Bus notifies all stakeholders
    → QA validates quality gate
    → Head signs off
    → CEO reports completion to Human
```

---

## Status Dashboard

| Component | Status | Notes |
|:----------|:-------|:------|
| 18 Department Profiles | Active | All deployed — 18 SOUL.md files complete |
| 55+ Specialist Agents | Active | SOUL.md files complete and deployed |
| Loop Runner | Active | Cron runs every 30 minutes |
| Central Bus (busd) | Legacy guide status; see current release audit | FastAPI v0.6, port 8099 — 5 endpoints, SQLite WAL, dual-queue backend (4,342 lines) |
| Central Bus — Monitor Watchdog | Partial | Functional but on JSONL backend; real-time mode + health probe pending |
| Central Bus — Dashboard | Partial | Project-state reader only; full pipeline observability (TeamHero UI) → v0.5.0 |
| Pipeline Dashboard | Planned | Q4 2026 target — TeamHero UI + Langfuse |
| OpenCode Integration | Active | 20 agents, 6 commands |
| Codex CLI Export | Active | 60 sub-agent TOML files |
| Open Design Bridge | Active | Read-only integration on port 41551 |

---

## Recommended Learning Path

For newcomers who want to understand the system thoroughly:

1. **Read this file** (you're here now)
2. **Read `ARCHITECTURE.md`** — understand the design principles
3. **Browse `profiles/INDEX.md`** — see all agents and their status
4. **Study `profiles/01-ceo/SOUL.md`** — understand how a Head profile works
5. **Study `profiles/05-architect/`** — see the most complete department
6. **Open `opencode.json`** — understand the full configuration
7. **Run `/status`** — see the system in action
8. **Submit a request** — experience the pipeline live

---

## Key Principles to Remember

- **Department Heads do not work** — they lead, delegate, and decide
- **Communication is structured** — Heads talk to Heads, sub-agents execute
- **Data flows autonomously** — Central Bus handles artifacts, not Heads
- **Handoffs are explicit** — every work transition is logged and auditable
- **Escalation is rare** — 80% of cases resolve through direct Head-to-Head
- **Status is published** — never wait to ask "what's the status"

---

## Common Questions

**Q: Can I talk directly to a sub-agent?**
A: No. All communication goes through Department Heads. Sub-agents receive
tasks from their Head and report back. This maintains clean accountability.

**Q: What if I don't know which department I need?**
A: Talk to the CEO (หนุมาน). The CEO will understand your request and route
it to the correct department.

**Q: How do I escalate a blocked task?**
A: If a sub-agent is blocked, they escalate to their Department Head. If the
Head cannot resolve it, they escalate to the Orchestrator (พี่วุฒิ). Critical
issues go to the CEO.

**Q: Is this production-ready?**
A: Yes. All 15 departments and their specialist agents are deployed and
active on Hermes Gateway. The Loop Runner operates on cron. The Central Bus
is the only major component still in design.

---

*SoloCorp OS — System First, Everything Follows*
