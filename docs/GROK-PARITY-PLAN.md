# SoloCorp OS × Grok Build — Parity Plan (→ OpenCode Gold)

**Status:** Phase 0 complete · Plan 1–3 not started  
**Created:** 2026-07-27  
**Approved:** 2026-07-27 (Owner)  
**Owner:** Engineering (ช่างฟูล) + Architect (พี่ทรงศักดิ์) · Sponsor: CEO  
**Goal:** ให้ Grok Build ทำงานกับ SoloCorp OS ได้**สมบูรณ์ระดับ OpenCode** ในขอบเขตที่ platform อนุญาต  
**Pack:** `.grok/` · Guide: `docs/GROK-SUPPORT.md` · Matrix: `docs/PLATFORM-COMPAT.md`

---

## 1. นิยาม “สมบูรณ์เหมือน OpenCode”

### 1.1 เป้าหมายที่ทำได้ (parity targets)

| มิติ | OpenCode วันนี้ | Grok วันนี้ | เป้าหมาย parity |
|:-----|:----------------|:------------|:----------------|
| Department / system agents | **21** ใน `.opencode/agents/` | **6** ใน `.grok/agents/` | **≥ 21** + COO + depts Active ที่ยังขาด (neteng, cybersec, psychology, coo, rd-lab) ตาม priority |
| Slash / pipeline commands | **19** ใน `opencode.json` | **7** skills | **19** skills ใน `.grok/skills/` |
| Default session identity | `default_agent: ceo-hanuman` | AGENTS.md เท่านั้น | Bootstrap + CEO-default behavior ใน skill + AGENTS |
| MCP SoloCorp | list/route/SOUL/commands | เหมือนกัน (7 tools) | + runtime ops (health, queue, handoff, dispatch) |
| Dept skills `@solocorp/*` | ผ่าน skills.paths | ไม่มี port | Port ทุก skill ที่ OpenCode เรียกได้ |
| Multi-dept pipeline | native multi-agent | depth 1 | Workflow / Orchestrator fan-out ชดเชย |
| Docs + smoke | มี | partial | Checklist + automated smoke ผ่าน |

### 1.2 Non-goals (platform limits — ไม่บังคับให้เท่า)

| จำกัดของ Grok | วิธีชดเชย |
|:--------------|:----------|
| ไม่มี `@mention` UI แบบ OpenCode | Natural-language triggers + `spawn subagent_type=…` + `/route` |
| Subagent depth = 1 | Parent (CEO/Orchestrator) fan-out ขนาน; children ไม่ spawn ต่อ |
| ไม่มี `opencode.json` command registry เดียวกัน | `.grok/skills/*/SKILL.md` เป็น source of truth ฝั่ง Grok |
| 55+ specialists ทุกตัวเป็น agent file | Heads ครบ + specialists ผ่าน MCP `get_team_members` / SOUL role-play ก่อน; package เฉพาะ critical ภายหลัง |

**Definition of Done (DoD) ระดับ org:**  
`docs/PLATFORM-COMPAT.md` แถว Grok = 🟢 Active และ matrix ใน PRD ตรงกับของจริงหลัง Plan 3

---

## 2. Gap Analysis (snapshot 2026-07-27)

### 2.1 Agents — มีใน OpenCode แต่ยังไม่มีใน Grok

| Agent | Role | Priority |
|:------|:-----|:--------:|
| `cfo-meetoo` | CFO | P0 |
| `cmo-mark` | CMO | P0 |
| `design-kreet` | Design | P0 |
| `ui-designer` | UI | P0 |
| `sales` | Sales | P1 |
| `support` | Support | P1 |
| `legal-tulya` | Legal | P1 |
| `web3-aywa` | Web3 | P1 |
| `content-creator-sek` | Content | P1 |
| `monitor-watchdog` | Monitor | P1 |
| `pipeline-auditor` | Pipeline audit | P1 |
| `routing-config-agent` | Routing config | P1 |
| `cron-pipeline` | Cron / schedule | P2 |
| `exception-triage` | Exception triage | P2 |
| `mcp-builder` | MCP builder | P2 |

**ขาดทั้ง OpenCode และ Grok (เติมฝั่ง Grok ใน Plan 1–2):**

| Agent (proposed) | Profile | Priority |
|:-----------------|:--------|:--------:|
| `coo-kit` | `02-coo` — L1–L3 gatekeeper | **P0** |
| `neteng-neet` | `16-neteng` | P2 |
| `cybersec-sai` | `17-cybersec` | P2 |
| `psychology-jit` | `18-psychology` | P2 |
| `rd-lab` (lead) | `19-rd-lab` | P2 |

**มีแล้วใน Grok (6):**  
`ceo-hanuman`, `orchestrator-wut`, `architect-songsak`, `product-produck`, `engineering-changful`, `qa`

### 2.2 Skills / commands — มีใน OpenCode แต่ยังไม่มีใน Grok

| Command | อยู่แล้ว (Grok) | ต้อง port |
|:--------|:---------------:|:---------:|
| `/pipeline` `/handoff` `/status` `/audit` `/deploy` `/brain` `/route` | ✅ | — |
| `/pipeline-bridge` | ❌ | ✅ |
| `/mirror-check` | ❌ | ✅ |
| `/bootstrap` | ❌ | ✅ |
| `/triage` | ❌ | ✅ |
| `/mirror` | ❌ | ✅ |
| `/orchestrate` | ❌ | ✅ |
| `/summary` | ❌ | ✅ |
| `/sprint-plan` | ❌ | ✅ |
| `/daily-ops` | ❌ | ✅ |
| `/eng-deploy` | ❌ | ✅ |
| `/budget-check` | ❌ | ✅ |
| `/smoke-test` | ❌ | ✅ |
| `/rfc-new` | ❌ | ✅ |

### 2.3 MCP / runtime

| Capability | วันนี้ | ช่องว่าง |
|:-----------|:------:|:---------|
| Departments / SOUL / route / commands | ✅ | — |
| Bus health / queue / dispatch | ❌ MCP | ต้อง shell หรือขยาย MCP |
| Create handoff record via API | ❌ MCP | ขยาย MCP หรือ skill เขียนไฟล์ |
| SkillHub `@solocorp/*` invoke | Bus API | Grok skill ยังไม่ wrap |

### 2.4 UX / session

| Capability | OpenCode | Grok gap |
|:-----------|:---------|:---------|
| Default CEO | `default_agent` | ต้อง enforce ผ่าน AGENTS + `/bootstrap` |
| `@ceo-hanuman` | native | ใช้ “ทำตัวเป็น CEO” / spawn |
| Auto session inject | `/bootstrap` | ยังไม่มี skill |

---

## 3. แผนพัฒนา 3 แพลน (Plan 1 → 2 → 3)

```
Phase 0 — Docs only              → ✅ เอกสารนี้ + ลิงก์ pack (2026-07-27)
Plan 1  — Foundation Parity      → agents + skills ครบชุด OpenCode core
Plan 2  — Runtime & Orchestration → MCP ops + workflows + export sync
Plan 3  — Hardening & Gold        → smoke, CI drift, matrix 🟢, acceptance
```

แต่ละแพลนมี: เป้าหมาย · งาน · deliverables · acceptance · ความเสี่ยง

---

### Phase 0 — เอกสารก่อน (เสร็จแล้ว)

| ไฟล์ | บทบาท |
|:-----|:------|
| **`docs/GROK-PARITY-PLAN.md`** | แผนเต็ม Plan 1/2/3 (source of truth) — ไฟล์นี้ |
| `docs/GROK-SUPPORT.md` | ลิงก์แผน + สถานะ Planned parity |
| `.grok/README.md` | ลิงก์แผน + ตาราง gap สั้นๆ |
| `docs/PLATFORM-COMPAT.md` | แถว Grok ชี้ parity plan; ยัง 🟡 จน Plan 3 |

**เกณฑ์ Phase 0:** Owner เปิดไฟล์นี้แล้วเห็นแผน 1–2–3 ครบ ✅

---

### Plan 1 — Foundation Parity (Core pack = OpenCode surface)

**สถานะ:** ⏳ Not started — รอ Owner สั่ง “เริ่ม Plan 1”  
**เป้า:** Grok เรียก Heads / system agents และ slash commands ได้ครบเท่า OpenCode ชุดหลัก โดยไม่ต้องพึ่ง OpenCode

#### งาน (ordered)

| # | Task | Owner | Output |
|:-:|:-----|:------|:-------|
| 1.1 | ออกแบบ template agent มาตรฐาน Grok (frontmatter + When to invoke + Boundaries + SOUL path) จาก `.grok/agents/ceo-hanuman.md` | Eng | ใช้ซ้ำทุก agent ใหม่ |
| 1.2 | เพิ่ม **P0 agents**: `coo-kit`, `cfo-meetoo`, `cmo-mark`, `design-kreet`, `ui-designer` | Eng | `.grok/agents/*.md` |
| 1.3 | เพิ่ม **P1 agents**: sales, support, legal, web3, content, monitor-watchdog, pipeline-auditor, routing-config-agent | Eng | `.grok/agents/*.md` |
| 1.4 | Port skills ที่ขาด → `.grok/skills/<name>/SKILL.md` (map จาก `opencode.json` + `.claude/commands/` + `skills/@solocorp/*`) | Eng | skill dirs ครบ 19 |
| 1.5 | อัปเดต `AGENTS.md` — ตาราง agent types ครบ + natural-language aliases (`@ceo` → spawn `ceo-hanuman`) | CEO/Eng | `AGENTS.md` |
| 1.6 | อัปเดต `.grok/README.md` + `docs/GROK-SUPPORT.md` รายการ agents/skills ใหม่ | Product/Eng | docs |
| 1.7 | Manual smoke: `grok inspect` + `/` เห็น skills + spawn 1 head ใหม่ | QA | checklist pass |

#### Deliverables

- `.grok/agents/` ≥ 21 files (OpenCode set + `coo-kit`)
- `.grok/skills/` = 7 เดิม + 12 ใหม่ = **19**
- Docs sync

#### Acceptance (Plan 1)

- [ ] `ls .grok/agents | wc -l` ≥ 21
- [ ] ทุก command ใน `opencode.json` → skill ชื่อเดียวกันใน `.grok/skills/`
- [ ] `/bootstrap`, `/daily-ops`, `/sprint-plan` รันได้ใน TUI (best-effort ถ้า service down ต้องบอกชัด)
- [ ] Spawn `coo-kit` / `cfo-meetoo` ได้จาก parent
- [ ] `docs/GROK-SUPPORT.md` ตาราง agents/skills ตรงของจริง

#### ประมาณการ

~2–4 วัน dev (port + เขียน agent จาก SOUL ที่มี — ไม่ invent identity ใหม่)

---

### Plan 2 — Runtime & Orchestration (ทำงานเป็นระบบ ไม่ใช่แค่ไฟล์)

**สถานะ:** ⏳ Blocked on Plan 1 acceptance  
**เป้า:** ชดเชย multi-agent depth และให้ runtime SoloCorp ใช้จาก Grok ได้ใกล้ OpenCode

#### งาน (ordered)

| # | Task | Owner | Output |
|:-:|:-----|:------|:-------|
| 2.1 | ขยาย **solocorp MCP** (read/ops ปลอดภัย): `health`, `queue_status`, `list_dispatches`, `create_handoff_note` (เขียนภายใต้ `bus/` ตาม SOP) | Architect + Eng | `solocorp_mcp/server.py` + tests |
| 2.2 | สร้าง **export script** `scripts/export-grok-agents.py` — sync จาก `profiles/*/SOUL.md` + `.opencode/agents/` → `.grok/agents/` (validate frontmatter) | Eng | script + `--validate-only` |
| 2.3 | เพิ่ม **Grok workflows** หรือ documented parent fan-out SOP สำหรับ `/pipeline` (ชดเชย depth-1) | Orchestrator + Eng | `.grok/workflows/*.rhai` หรือ SOP |
| 2.4 | Port / wrap **SkillHub** skills ที่ hit Bus API ให้ skill Grok เรียก HTTP หรือ python module เดียวกับ OpenCode | Eng | skills เรียก runtime จริง |
| 2.5 | Personas ครบ Heads ที่เหลือใน `.grok/personas/` | Eng | personas |
| 2.6 | P2 agents: cron-pipeline, exception-triage, mcp-builder, neteng, cybersec, psychology, rd-lab | Eng | agents |
| 2.7 | อัป `PLATFORM-COMPAT.md` แถว Grok → skills/agents counts จริง | Product | docs |

#### Deliverables

- MCP tools ชุด runtime (documented ใน `solocorp_mcp/README.md`)
- `export-grok-agents.py` ใน local validate
- Workflow หรือ SOP fan-out สำหรับ `/pipeline`
- Skills ชุด dept เรียก bus ได้เมื่อ bus up

#### Acceptance (Plan 2)

- [ ] `grok mcp list` เห็น tools ใหม่; `health` ตรงกับ `curl :8099/v1/health`
- [ ] `python scripts/export-grok-agents.py --validate-only` ผ่าน
- [ ] `/pipeline <feature>` ใช้ orchestrator pattern (plan → eng → qa) โดย parent เป็นตัว spawn
- [ ] `/status` ใช้ MCP health ได้ (fallback curl ยังได้)
- [ ] ไม่มี secret ถูก hardcode เพิ่มใน config

#### ประมาณการ

~1–2 สัปดาห์

---

### Plan 3 — Hardening & Gold Status

**สถานะ:** ⏳ Blocked on Plan 2 acceptance  
**เป้า:** ประกาศ Grok = 🟢 Active เทียบ OpenCode ได้ใน matrix พร้อมหลักฐาน

#### งาน (ordered)

| # | Task | Owner | Output |
|:-:|:-----|:------|:-------|
| 3.1 | **Grok smoke suite** `scripts/smoke-grok-pack.sh` — ตรวจ agents count, skills count, frontmatter, MCP import, skill name ∩ opencode commands | QA + Eng | script + exit codes |
| 3.2 | ผูก smoke เข้า CI เมื่อแตะ `.grok/**` | Eng | CI |
| 3.3 | **Mention shim doc** — ตาราง `@name` (OpenCode) → `subagent_type` / NL phrase (Grok) ใน `docs/GROK-SUPPORT.md` | Product | docs |
| 3.4 | Drift guard: ถ้า `opencode.json` เพิ่ม command ใหม่ แต่ไม่มี `.grok/skills/<name>` → fail validate | Eng | export/validate |
| 3.5 | อัป PRD matrix + `PLATFORM-COMPAT.md` → Grok 🟢 Active | Product | docs |
| 3.6 | Acceptance demo script (Owner-facing): bootstrap → route → handoff → pipeline → status → summary | CEO/QA | demo section ใน GROK-SUPPORT |
| 3.7 | บันทึก residual gaps (depth-1, no @mention) ชัดใน Compatibility limits — ไม่ overclaim | Architect | docs |

#### Deliverables

- Automated smoke + CI
- Matrix 🟢
- Owner demo path 5 นาที

#### Acceptance (Plan 3) — Gold

- [ ] Smoke script ผ่านบน clean clone + `.venv`
- [ ] Command parity 100% กับ `opencode.json` `command` keys
- [ ] Agent parity ≥ OpenCode `.opencode/agents/` set + `coo-kit`
- [ ] `/bootstrap` → context inject อ่านได้
- [ ] End-to-end demo บันทึกใน session log / brain
- [ ] `PLATFORM-COMPAT.md` Grok = 🟢 และวันที่อัปเดต
- [ ] Residual limits ยังระบุตรงความจริงของ platform

#### ประมาณการ

~3–5 วัน หลัง Plan 2 เสร็จ

---

## 4. ลำดับการทำงาน (execution order)

```text
[Phase 0 — docs] ✅ 2026-07-27
  docs/GROK-PARITY-PLAN.md
  links in GROK-SUPPORT / .grok/README / PLATFORM-COMPAT

[Plan 1]  ──► agents + skills parity ──► manual smoke
[Plan 2]  ──► MCP + export + workflows ──► runtime smoke
[Plan 3]  ──► CI + matrix 🟢 + Owner demo
```

**กฎ:** ไม่เริ่ม Plan N+1 จนกว่า Acceptance ของ Plan N ผ่าน (ยกเว้น Owner เร่ง P0 บางข้อข้ามแบบมีบันทึก)

---

## 5. Mapping ไฟล์สำคัญ

| ทำอะไร | แตะไฟล์ |
|:-------|:--------|
| Agents | `.grok/agents/<id>.md` ← อ้าง `profiles/**/SOUL.md`, mirror โครงสร้าง `.opencode/agents/` |
| Skills | `.grok/skills/<cmd>/SKILL.md` ← `opencode.json` commands + `skills/@solocorp/**` |
| MCP | `solocorp_mcp/server.py`, `.grok/config.toml` |
| Session rules | `AGENTS.md`, `rules/*` |
| Export | `scripts/export-grok-agents.py` (ใหม่ — Plan 2) |
| Smoke | `scripts/smoke-grok-pack.sh` (ใหม่ — Plan 3) |
| Docs | `docs/GROK-SUPPORT.md`, `.grok/README.md`, `docs/PLATFORM-COMPAT.md`, PRD multi-platform |

---

## 6. มาตรฐาน agent file (Grok)

```yaml
---
name: <subagent_type>
description: >
  <1–3 lines: who + when to invoke + triggers>
prompt_mode: full
model: inherit
permission_mode: default
agents_md: true
---
```

Body บังคับมี: When to invoke · Pillars/Responsibilities · Boundaries · Always read (SOUL path) · Output format  
**ห้าม** copy identity คนละแผนก — ต้องอ่าน SOUL จริงของ profile นั้น

---

## 7. มาตรฐาน skill file (Grok)

```yaml
---
name: <command-name>          # ตรงกับ opencode.json key
description: >
  ...
argument-hint: "..."
user-invocable: true
---
```

Body: Inputs · Preconditions · Steps (คำสั่งจริง) · Output format · Rules  
ถ้า OpenCode ชี้ไปที่ Bus API / python module — Grok skill ต้องชี้จุดเดียวกัน

---

## 8. Risks & mitigations

| Risk | Impact | Mitigation |
|:-----|:------:|:-----------|
| Agent เยอะ → context / discoverability | Medium | description triggers ชัด; `/route` แนะนำ agent |
| Depth-1 ทำให้ pipeline อ่อน | High | Orchestrator parent only spawns; workflow doc |
| Drift OpenCode ↔ Grok | High | export validate + CI (Plan 3) |
| MCP write ลง bus ผิด SOP | High | scope auth + dry-run + เขียนเฉพาะ path อนุญาต |
| Overclaim “เต็ม 100%” | Med | เก็บ non-goals ใน docs ตลอด |

---

## 9. Success metrics

| Metric | ตอนนี้ | หลัง Plan 1 | หลัง Plan 2 | หลัง Plan 3 |
|:-------|:------:|:-----------:|:-----------:|:-----------:|
| Grok agents | 6 | ≥ 21 | ≥ 25 | ≥ 25 + validate |
| Grok skills | 7 | 19 | 19 (runtime-backed) | 19 + CI |
| MCP tools (solocorp) | 7 | 7 | ≥ 11 | ≥ 11 |
| PLATFORM-COMPAT Grok | 🟡 | 🟡/🟢 partial | 🟡→🟢 candidate | 🟢 Active |
| Command parity vs OpenCode | ~37% | 100% names | 100% + live | 100% + smoke |

---

## 10. Next action

1. **Phase 0 เสร็จแล้ว** — เอกสารนี้อยู่ใน repo
2. **ยังไม่ implement Plan 1** จนกว่า Owner ยืนยัน **“เริ่ม Plan 1”**
3. เมื่อเริ่ม Plan 1:
   - สร้าง change `feat/grok-parity-plan1`
   - ทำ 1.2 → 1.4 ก่อน (agents P0 + skills ที่ใช้บ่อย: `bootstrap`, `summary`, `daily-ops`, `mirror-check`)
   - Manual smoke แล้วค่อย P1 agents

---

## Related

| Doc | บทบาท |
|:----|:------|
| `.grok/README.md` | Pack overview |
| `docs/GROK-SUPPORT.md` | Support guide + limits |
| `docs/PLATFORM-COMPAT.md` | Cross-platform matrix |
| `docs/prds/PRD-Multi-Platform-Compatibility-v1.0.md` | PRD goals G1–G5 |
| `opencode.json` | Gold command/agent reference |
| `AGENTS.md` | Session entry for Grok |

---

*SoloCorp OS — System First, Everything Follows*  
*Document type: Development Plan · Not an ADR · Implementation gated on Owner go for each Plan*
