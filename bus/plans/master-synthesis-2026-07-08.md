# 🏢 SoloCorp Master Synthesis — แผนเติบโตทรงพลัง

> **เป้าหมาย:** เปลี่ยน 6 วัตถุดิบภายนอก → ขีดความสามารถภายในของ SoloCorp  
> **กลยุทธ์:** ศึกษา → ปรับใช้ → ขยายผล → สร้างเป็น DNA องค์กร

---

## สารบัญ

1. [ภาพรวม — 6 วัตถุดิบ → 6 ขีดความสามารถ](#1-ภาพรวม--6-วัตถุดิบ--6-ขีดความสามารถ)
2. [Workflow หลัก — การไหลของงาน](#2-workflow-หลัก--การไหลของงาน)
3. [Department Tasks Breakdown](#3-department-tasks-breakdown)
4. [Handoff Protocol](#4-handoff-protocol)
5. [Timeline & Milestones](#5-timeline--milestones)
6. [KPIs — วัดความทรงพลัง](#6-kpis--วัดความทรงพลัง)

---

## 1. ภาพรวม — 6 วัตถุดิบ → 6 ขีดความสามารถ

```
วัตถุดิบภายนอก                 ขีดความสามารถภายใน SoloCorp
─────────────────             ─────────────────────────────
📄 OmniScientist      ──→    🔬 R&D Lab → Automated Research Pipeline
🎭 Agency Agents      ──→    🧠 Agent Personality System v2
📦 Antigravity Skills ──→    📚 SkillHub Registry ( содержательный)
🛠️ Awesome Dev Agents ──→   ⚙️ Engineering Toolchain
🔴 HackAgent          ──→    🛡️ Security Red Team Program
🧩 SkillHub           ──→    🏗️ Enterprise Skill Infrastructure
```

| วัตถุดิบ | เจ้าของหลัก | แผนกสนับสนุน | มูลค่าเพิ่ม |
|:--------|:-----------|:-------------|:-----------|
| **OmniScientist** | R&D Lab (#19) | Product, Engineering | AI research automation |
| **Agency Agents** | R&D Lab (#19) | All 19 departments | Better agent personality |
| **Antigravity Skills** | SkillHub Admin (Architect #05) | All depts | 1,935 ready skills |
| **Awesome Dev Agents** | Engineering (#07) | R&D Lab, QA | 32 tools comparison |
| **HackAgent** | Cyber Security (#17) | R&D Lab, Engineering | Automated security testing |
| **SkillHub** | Architect (#05) | All depts | Central skill registry |

---

## 2. Workflow หลัก — การไหลของงาน

```
                    ┌─────────────────────────────┐
                    │      Dr.solodev (Owner)      │
                    │     สั่ง: "สังเคราะห์ให้หมด"    │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │    CEO (หนุมาน)               │
                    │    แตกงาน → มอบหมาย          │
                    └────────────┬────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
   ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Orchestrator    │  │   R&D Lab    │  │   Architect  │
   │  (พี่วุฒิ)        │  │  (วิจัย/ปรับ)  │  │  (พี่ทรงศักดิ์) │
   │  ตั้ง Pipeline   │  │  ศึกษา→Adapt  │  │  SkillHub    │
   └──────┬───────────┘  └──────┬───────┘  └──────┬───────┘
          │                      │                 │
          └──────────────────────┼─────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   Department ปลายทาง     │
                    │   Engineering / Security │
                    │   Product / Design / QA  │
                    └─────────────────────────┘
```

---

## 3. Department Tasks Breakdown

### 🔬 R&D Lab (#19) — วิจัยและปรับใช้

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| RD-01 | **ศึกษา OmniScientist** — อ่าน 7 papers → สรุป 1 หน้า/paper | AI Research Scientist | → Knowledge Curator (บันทึก) → Product (roadmap) |
| RD-02 | **Deep Ideation** — สร้าง SoloCorp concept network + generate research ideas | AI Research Scientist + Prototyper | → Lead Researcher (คัดเลือก) → CEO (อนุมัติ) |
| RD-03 | **AgentExpt** — ออกแบบ automated experiment system | Experiment Designer + Tool Smith | → R&D Lab ใช้ภายใน → ขยายให้ Product |
| RD-04 | **MirrorMind** — expert tacit knowledge → ปรับปรุง SOUL.md content | AI Research Scientist + Knowledge Curator | → All Dept Heads (ปรับ SOUL.md) |
| RD-05 | **Agency Agents Analysis** — 210 agents → catalog → extract patterns | Knowledge Curator + Wild Card | → All Dept Heads (pattern ตรง department) |
| RD-06 | **Antigravity Curation** — เลือก skills ที่ตรง SoloCorp | Knowledge Curator | → SkillHub Admin (publish) |
| RD-07 | **Dev Agents Evaluation** — ทดลอง 5 tools/week → รายงาน | Prototyper + Tool Smith | → Engineering (เลือกใช้) |

### 🏗️ Architect (#05) — SkillHub + Infrastructure

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| AR-01 | **Deploy SkillHub** — PostgreSQL + Redis + MinIO + API + Web | SkillHub Admin | → ส่ง URL ให้ CEO + All Dept Heads |
| AR-02 | **สร้าง Namespace** — `@solocorp/*` ตาม department | SkillHub Admin | → แจ้ง Dept Head แต่ละ department |
| AR-03 | **ตั้ง RBAC** — Owner/Admin/Member ตาม department structure | SkillHub Admin | → อนุมัติโดย Architect |
| AR-04 | **Publish curated skills** — จาก Antigravity + Agency Agents | SkillHub Admin | → R&D Lab (review) → All depts (ใช้) |
| AR-05 | **Integrate SkillHub กับ Pipeline** — auto-publish after build | Pipeline Auditor + Routing Agent | → Orchestrator |

### ⚙️ Engineering (#07) — Toolchain + Integration

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| EN-01 | **Evaluate 32 Dev Agents** — ทดลอง Aider, Codex, Cursor, Windsurf | Engineering Team | → R&D Lab (report) → CEO (เลือกมาตรฐาน) |
| EN-02 | **Integrate SkillHub MCP tools** — เพิ่ม skillhub_search/install tools | Engineering Team | → QA (test) → Deploy |
| EN-03 | **Create Dev Environment Standard** — Docker + devcontainer สำหรับทุก department | Engineering Team | → All depts (ใช้) |
| EN-04 | **Support R&D Lab prototypes** — ยืม dev resources เมื่อ R&D Lab ขอ | Engineering Team | → R&D Lab (request) |

### 🛡️ Cyber Security (#17) — Red Team + HackAgent

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| CS-01 | **ติดตั้ง HackAgent** + configure | Red Team Operator | → Sai (review) |
| CS-02 | **Red Team Campaign #1** — MCP Server + Central Bus | Red Team Operator | → Sai (report) → CEO (review) |
| CS-03 | **Security Scan Antigravity Skills** — ก่อน publish ลง SkillHub | Vulnerability Assessor + Red Team | → SkillHub Admin (block unsafe) |
| CS-04 | **Purple Team with R&D Lab** — security review of new prototypes | Security Engineer + R&D Lab | → CEO |

### 🎯 Product (#06) — Roadmap + Feature

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| PR-01 | **Integrate OmniScientist findings** เข้า Product Roadmap | Product Manager | → CEO (approve) |
| PR-02 | **Define SkillHub usage policy** — ใช้ skill ยังไงใน product | Product Manager | → Architect + Legal |

### 🎨 Design (#08) — SOUL.md Visual + UX

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| DS-01 | **Apply SOUL.md Template v2** — ปรับ design system ตาม vibe/color/emoji | Design Team | → All Dept Heads |
| DS-02 | **Design SkillHub UI extension** — ถ้าต้อง customize | Design Team | → Engineering |

### ✅ Quality Assurance (#10) — Testing

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| QA-01 | **Test SkillHub deployment** — API smoke test + namespace workflow | QA Team | → Architect (fix bugs) |
| QA-02 | **Validate SOUL.md v2 rollout** — ทุก department มี profile ครบ | QA Team | → CEO (report) |

### 📋 Orchestrator (#04) — Pipeline + Coordination

| # | งาน | มอบหมาย | ส่งต่อ |
|:-:|:----|:--------|:-------|
| OR-01 | **ตั้ง Pipeline สำหรับงานทั้งหมด** — `/pipeline rd-synthesis` | Orchestrator | → All depts |
| OR-02 | **Monitor progress** — ตาม milestone ทุก department | Orchestrator | → CEO (weekly brief) |

---

## 4. Handoff Protocol

```
RD-01 ──→ Product ──→ CEO
RD-02 ──→ CEO ──→ (อนุมัติ) ──→ All depts
RD-03 ──→ R&D Lab internal ──→ Product
RD-04 ──→ All Dept Heads
RD-05 ──→ All Dept Heads
RD-06 ──→ SkillHub Admin
RD-07 ──→ Engineering ──→ CEO

AR-01 ──→ CEO + All Dept Heads
AR-02 ──→ All Dept Heads
AR-03 ──→ Architect
AR-04 ──→ R&D Lab (review) ──→ All depts
AR-05 ──→ Orchestrator

EN-01 ──→ R&D Lab ──→ CEO
EN-02 ──→ QA ──→ Deploy
EN-03 ──→ All depts
EN-04 ──→ R&D Lab

CS-01 ──→ Sai
CS-02 ──→ Sai ──→ CEO
CS-03 ──→ SkillHub Admin
CS-04 ──→ CEO

PR-01 ──→ CEO
PR-02 ──→ Architect + Legal

DS-01 ──→ All Dept Heads
DS-02 ──→ Engineering

QA-01 ──→ Architect
QA-02 ──→ CEO

OR-01 ──→ All depts
OR-02 ──→ CEO
```

---

## 5. Timeline & Milestones

### Sprint 1: Foundation (สัปดาห์ 1-2)

| Week | งาน | Department |
|:----:|:----|:----------|
| 1 | RD-01: ศึกษา OmniScientist papers | R&D Lab |
| 1 | AR-01: Deploy SkillHub | Architect |
| 1 | CS-01: ติดตั้ง HackAgent | Security |
| 2 | RD-05: Agency Agents catalog | R&D Lab |
| 2 | AR-02/03: Namespace + RBAC | Architect |
| 2 | EN-01: เริ่ม evaluate dev agents | Engineering |

### Sprint 2: Integration (สัปดาห์ 3-4)

| Week | งาน | Department |
|:----:|:----|:----------|
| 3 | RD-02: Deep Ideation | R&D Lab |
| 3 | AR-04: Publish skills | Architect |
| 3 | CS-02: Red Team Campaign #1 | Security |
| 4 | RD-04: MirrorMind → SOUL.md | R&D Lab + All Depts |
| 4 | DS-01: SOUL.md v2 rollout | Design + All Depts |

### Sprint 3: Production (สัปดาห์ 5-6)

| Week | งาน | Department |
|:----:|:----|:----------|
| 5 | EN-02: MCP tools for SkillHub | Engineering |
| 5 | QA-01: SkillHub test | QA |
| 6 | OR-02: Progress review | Orchestrator → CEO |
| 6 | 🎯 **SoloCorp พร้อมเปิดประตูรับแขก** | All depts |

---

## 6. KPIs — วัดความทรงพลัง

| KPI | เป้าหมาย | วัดจาก |
|:----|:---------|:-------|
| **SkillHub Packages** | 50+ skills ใน namespace ต่างๆ | SkillHub API |
| **SOUL.md v2 Rollout** | 19/19 departments ใช้ template ใหม่ | QA audit |
| **Red Team Campaigns** | 1 campaign/quarter | Security report |
| **R&D Lab Outputs** | 1 research report/สัปดาห์ | Knowledge Base |
| **Dev Tools Standardized** | 3-5 tools เป็นมาตรฐานองค์กร | Engineering report |
| **OmniScientist Insights** | 7 papers summarized → 3 action items | Product roadmap |

---

## Appendix — Quick Reference

```
/pipeline rd-synthesis    — รัน pipeline หลัก (Orchestrator)
/handoff @architect @engineering "SkillHub MCP tools" — ตัวอย่าง handoff
/status  — เช็คความคืบหน้าทุก department
/audit synthesis   — ตรวจ compliance
/skillhub publish @solocorp/rd/soul-template-v2   — Publish skill
```

---

*SoloCorp OS — System First, Everything Follows*  
*Master Synthesis v1.0 — 6 วัตถุดิบ → 6 ขีดความสามารถ → 1 องค์กรที่ทรงพลัง*
