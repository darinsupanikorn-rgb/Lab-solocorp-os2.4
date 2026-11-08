# ADR-016: Behavior-Centric Routing + Harness Handbook

**วันที่:** 2026-07-20  
**สถานะ:** Accepted ✅  
**Owner:** CEO หนุมาน  
**设计师:** Architect พี่ทรงศักดิ์ + Product โปรดัค  
**來源:** Harness Handbook (Wang et al., 2026) — arXiv:2607.13285

---

## บริบท

SoloCorp OS มีระบบ routing ปัจจุบันที่ route request ผ่าน 3 tiers:

1. **Tier 0a/0b** — Governance/AO message routing
2. **Tier 1** — Keyword matching (23 rules ใน `routing_rules.json`)
3. **Tier 2** — Semantic matching (TF-IDF + cosine similarity)
4. **Tier 3** — CEO fallback

ปัญหาที่พบ:
- **Route ตาม "คำพูด" ไม่ใช่ "ความตั้งใจ"** — keyword matching มี false positive สูง
- **Thai language routing Weak** — regex keyword ไม่ครอบคลุมภาษาไทย
- **Accuracy ประมาณ 65-70%** — ต้องส่ง CEO review บ่อยเกินจำเป็น
- **ไม่มี behavior abstraction layer** — request ที่ complex (ข้ามหลาย department) route ไม่ตรง
- **ระบบ routing ยิ่งโต ยิ่งยากต่อการ maintain** — 23 rules แล้ว ต้องเพิ่มอีกเรื่อยๆ

## แนวคิดจาก Harness Handbook

Harness Handbook (Wang et al., Tencent + Indiana University, July 2026) เสนอแนวทาง:

> **Behavior-Centric Representation** — จัดระเบียบ knowledge รอบ behaviors (สิ่งที่ระบบทำ) 
> แทนที่จะจัดรอบ files/modules (ที่ code อยู่)
>
> **Behavior-Guided Progressive Disclosure (BGPD)** — พา coding agent จาก behavior 
> ระดับสูง → ลงไปหา implementation details ที่เกี่ยวข้อง

เรา adapt มาใช้กับ SoloCorp OS ในรูปแบบ **Behavior-Centric Routing**:
- request → classify behavior intent → route ไป department ที่ถูกต้อง
- confidence-based: ≥ 90% route อัตโนมัติ, < 90% ส่ง CEO review
- add-on layer ไม่破壞ระบบเดิม

## ข้อตกลง (Decision)

### 1. Architecture Change

```
ก่อน:  [Message] → Keyword (T1) → Semantic (T2) → CEO (T3)
หลัง:  [Message] → Behavior Classifier (NEW Tier 0)
                         ↓
               ≥ 0.90 → Route to primary_dept
               < 0.90 → Keyword (T1) → Semantic (T2) → CEO (T3)
```

**Non-destructive** — `routing_rules.json`, `RoutingEngine`, `route()` ไม่ได้แตะ
Behavior layer เพิ่มเป็น Tier 0 ก่อนระบบเดิม

### 2. Key Decisions

| เรื่อง | Decision | Owner |
|:------|:---------|:------|
| **Taxonomy Size** | 26 behaviors (8 domains) | Dr.solodev ✅ |
| **Confidence Threshold** | ≥ 90% → route, < 90% → CEO review | Dr.solodev ✅ |
| **Migration Strategy** | Add-on (non-destructive) | Dr.solodev ✅ |
| **Implementation Priority** | Data Schema ก่อน → Classifier ตาม | Dr.solodev ✅ |

### 3. Implementation Plan (4 Weeks)

| Phase | สัปดาห์ | อะไร | ใคร |
|:------|:-------|:-----|:----|
| Phase 1 | W1 | Data Schema + 26 behaviors seed + ADR | `@architect-songsak` |
| Phase 2 | W2 | Behavior Classifier module | `@changful` |
| Phase 3 | W3 | Router integration + tests | `@changful` + `@qa` |
| Phase 4 | W4 | AAR + iterate | `@orchestrator-wut` |

---

## Appendix A — SoloCorp OS Harness Handbook

> คู่มือ behavior-level ของ SoloCorp OS — version 1.0 (July 2026)
>
> เป้าหมาย: ทำให้ทั้งมนุษย์ (Dr.Solodev) และ coding agent (Claude Code, Copilot, 
> opencode, Codex CLI) หาตำแหน่งโค้ดที่ต้องแก้ได้เร็วขึ้น เมื่อ request คือ 
> "เปลี่ยนพฤติกรรม X" ไม่ใช่ "แก้ไฟล์ Y"
>
> **Living Document** — ต้อง update ทุกครั้งที่มีการเปลี่ยนแปลง routing/behavior

### A1 — System Overview

SoloCorp OS คือ **agent harness** ที่ครอบ AI model ไว้ด้วยชั้นการจัดการ 4 ส่วน:

| ชั้น | หน้าที่ | Home ในโค้ด |
|---|---|---|
| Prompt / Identity | นิยามตัวตนของแต่ละ Head/Specialist | `profiles/*/SOUL.md` |
| State | ความจำ session, audit trail, decision log | `brain/`, `bus/`, `decisions/` |
| Tool Invocation | เลือกและเรียกใช้ skill ที่เหมาะกับงาน | `skills/` (93+ รายการ) |
| Execution Flow | ลำดับการรัน, cron, message passing | `loop_runner/`, `central_bus/`, `govctl_cli/` |

Chain of command:
```
Human → CEO → C-Level (CFO/CMO/Orch) → Architect → 18 Department Heads → 55+ Specialists
```

Two-Tier Architecture:
- **Control layer** (sync-ish, Head-to-Head): status, goals, exceptions, approvals, handoffs
- **Data layer** (async, ผ่าน Central Bus): code, designs, reports, raw outputs

### A2 — Behavior Units (7 Behaviors)

#### B1 — Head-to-Head Handoff
เมื่อ department หนึ่งส่งงานต่อให้อีก department (เช่น Product → Engineering)
- **ที่เกี่ยวข้อง:** `govctl_cli/` (คำสั่ง `/handoff`), `central_bus/`
- **คำถามที่ Handbook ควรตอบ:** handoff ที่ค้างจะ timeout ยังไง? ใคร escalate?
- **Owner:** `@orchestrator-wut`
- **สถานะ:** ✅ Active

#### B2 — Central Bus Message Routing
Data layer ที่ specialist เขียนงานเข้าคิว แล้วแจ้ง specialist ปลายทาง
- **ที่เกี่ยวข้อง:** `central_bus/` (FastAPI daemon + SQLite WAL)
- **คำถามที่ Handbook ควรตอบ:** message schema เป็นยังไง? retry policy เมื่อ consumer ล่ม?
- **Owner:** `@architect-songsak`
- **สถานะ:** 🔄 กำลังอัปเกรดเป็น Behavior-Centric (ADR-016)

#### B3 — Guard Gate / RFC → ADR Governance
xGov protocol: RFC → ADR → Guard Gates ก่อนเปลี่ยนแปลงระบบ
- **ที่เกี่ยวข้อง:** `gov/`, `govctl_cli/`, `decisions/`
- **คำถามที่ Handbook ควรตอบ:** อะไรต้องผ่าน Guard Gate? อะไรแก้ตรงได้เลย?
- **Owner:** `@architect-songsak`
- **สถานะ:** ✅ Active

#### B4 — Loop Runner (Cron Auto-pilot)
รันงานอัตโนมัติทุก 30 นาที
- **ที่เกี่ยวข้อง:** `loop_runner/`
- **คำถามที่ Handbook ควรตอบ:** ถ้า loop ทำงานค้าง recover ยังไง? มี dead-man's switch ไหม?
- **Owner:** `@orchestrator-wut`
- **สถานะ:** ✅ Active

#### B5 — Skill Resolution
Agent เลือกใช้ skill ไหนจาก 93+ รายการ เมื่อไหร่ ตาม department ใด
- **ที่เกี่ยวข้อง:** `skills/`, `profiles/*/SOUL.md`
- **คำถามที่ Handbook ควรตอบ:** fallback ถ้า skill ไม่มี? skill ชนกันได้ไหม?
- **Owner:** `@architect-songsak`
- **สถานะ:** ✅ Active

#### B6 — Qualification Gate (Product Packs)
3-question gate ก่อนให้ operator เข้าถึง CFO/Legal/Content Creator Pack
- **ที่เกี่ยวข้อง:** `profiles/` (pack heads: `@cfo-meetoo`, `@legal-tulya`, `@content-creator-sek`)
- **คำถามที่ Handbook ควรตอบ:** เกณฑ์ผ่าน/ไม่ผ่านคืออะไร? ใคร review edge case?
- **Owner:** `@product-produck`
- **สถานะ:** ⚠️ Needs formalization

#### B7 — Escalation Path
เมื่อ specialist ทำงานไม่ผ่าน QA หรือชนกับ Guard Gate
- **ที่เกี่ยวข้อง:** Exception Triage — `profiles/05-architect/`, `central_bus/`
- **Owner:** `@architect-songsak`
- **สถานะ:** ⚠️ Needs consolidation (ปัจจุบันกระจายในหลายที่)

### A3 — Behavior Taxonomy (26 Behaviors)

| Domain | Behaviors | Primary Dept |
|:-------|:----------|:-------------|
| **leadership** | `vision_strategy`, `owner_decision` | CEO |
| **finance** | `budget_approval`, `cost_analysis` | CFO |
| **marketing** | `campaign_management`, `brand_strategy` | CMO |
| **content** | `content_production` | Content Creator |
| **operations** | `pipeline_coordination` | Orchestrator |
| **architecture** | `architecture_design`, `routing_monitoring` | Architect |
| **product** | `feature_definition`, `roadmap_planning` | Product |
| **engineering** | `backend_development`, `frontend_development`, `bug_fixing` | Engineering |
| **design** | `visual_design`, `ux_research` | Design |
| **quality** | `qa_testing` | QA |
| **sales** | `sales_deal` | Sales |
| **support** | `customer_support` | Support |
| **legal** | `legal_compliance`, `contract_management` | Legal |
| **web3** | `smart_contract_defi` | Web3 |
| **network** | `network_operations` | NetEng |
| **security** | `security_incident` | CyberSec |
| **psychology** | `behavioral_research` | Psychology |

### A4 — State Register

| State | เก็บที่ | Scope | อายุ |
|:------|:--------|:------|:-----|
| Session memory | `brain/` | ต่อ conversation | จบ session |
| Audit trail | `bus/` | ระบบทั้งหมด | ถาวร |
| Architecture decisions | `decisions/` (ADRs) | ถาวร | ถาวร |
| Message queue | Central Bus SQLite WAL | runtime | ระยะสั้น |
| Routing rules | `bus/system/routing_rules.json` | ระบบ | ถาวร |
| Behavior taxonomy | `central_bus/` DB | ระบบ | ถาวร (migration) |

### A5 — วิธีใช้ Handbook (BGPD Workflow)

เมื่อจะขอให้ agent แก้ไขพฤติกรรมของระบบ:

1. **ระบุ behavior unit** ที่ request แตะถึง (จากตาราง A2) — ไม่ใช่เริ่มจากไฟล์
2. **เปิด Implementation Sites** ของ behavior นั้น — ดู path ที่เกี่ยวข้อง
3. **เช็คว่า request ข้าม behavior unit หลายอันไหม** (เช่น เพิ่ม department ใหม่ = B1, B5, B6) — จุดที่งานมักหลุดมือ
4. **อัปเดต Handbook หลังแก้เสร็จ** — ให้ Implementation Sites ตรงกับของจริงเสมอ

### A6 — Next Steps

- [ ] B2: Data Schema + 26 behaviors seed — `@architect-songsak` ✅ Done
- [ ] B2: Behavior Classifier module — `@changful` 📅 W2
- [ ] B6: Formalize Qualification Gate — `@product-produck` 📅 TBD
- [ ] B7: Consolidate Escalation Path — `@architect-songsak` 📅 TBD
- [ ] Living doc auto-diff: script ที่ diff Handbook vs โครงสร้างจริง ป้องกันล้าสมัย

---

## ผลกระทบ

### Positive
- **Routing accuracy เพิ่ม** — จาก 65-70% → ≥ 90% (คาดการณ์)
- **CEO review volume ลดลง** — จาก 100% → < 10% ที่ต้อง review
- **Non-destructive** — ระบบเก่ายังทำงานได้ 100% ระหว่าง migration
- **Harness Handbook เป็น living doc** — behavior-level visibility ทั้งระบบ

### Risks & Mitigation

| Risk | Impact | Mitigation |
|:-----|:-------|:-----------|
| Behavior classifier  accuracy ต่ำ | High | 90% threshold + fallback ไป keyword/Semantic |
| 26 behaviors ไม่ครอบคลุม | Medium | Extendable taxonomy — เพิ่มได้ผ่าน config |
| Migration ล่าช้า | Low | Add-on — ไม่ blocking ระบบเดิม |
| Handbook ล้าสมัย | Medium | Next step: auto-diff script |

### ต้นทุน (Token/Time)

- **Behavior Classification:** embedding + linear classifier (target < 50ms latency)
- **ไม่ใช้ LLM สำหรับ classify** — เร็วและถูกกว่า
- **Migration:** 4 weeks, backward compatible ตลอดทาง

---

## 脚注

1. Harness Handbook paper: https://arxiv.org/abs/2607.13285
2. SoloCorp OS Central Bus: `central_bus/`
3. Routing Rules: `bus/system/routing_rules.json`
4. Department Profiles: `profiles/INDEX.md`
