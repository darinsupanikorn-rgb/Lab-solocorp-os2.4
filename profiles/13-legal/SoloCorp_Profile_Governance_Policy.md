# SoloCorp Profile Governance Policy
## ฉบับที่ 1.0 — มีผลบังคับใช้วันที่ 22 มิถุนายน 2026

**ผู้จัดทำ:** Legal (คุณตุลย์) — Head of Legal & Governance, SoloCorp OS  
**ผู้อนุมัติ:** CEO (หนุมาน)  
**ประเภทเอกสาร:** นโยบายองค์กร (Corporate Policy)  
**อายุเอกสาร:** ทบทวนทุก 90 วัน หรือเมื่อมีการแก้ไข Org Chart

---

## สารบัญ

1. [หลักการและเหตุผล](#1-หลักการและเหตุผล)
2. [ขอบเขตการบังคับใช้](#2-ขอบเขตการบังคับใช้)
3. [Naming Standard (มาตรฐานการตั้งชื่อ Profile)](#3-naming-standard-มาตรฐานการตั้งชื่อ-profile)
4. [SoloCorp Profile Charter](#4-solocorp-profile-charter)
5. [Accountability & Ownership](#5-accountability--ownership)
6. [Resolution Protocol (เมื่อเกิด Conflict)](#6-resolution-protocol-เมื่อเกิด-conflict)
7. [Change Management (การ Rename/เพิ่ม/ลบ Profile)](#7-change-management-การ-renameเพิ่มลบ-profile)
8. [การวิเคราะห์ Compliance ของ Profiles ปัจจุบัน](#8-การวิเคราะห์-compliance-ของ-profiles-ปัจจุบัน)
9. [คำสั่งให้ดำเนินการ (Directives)](#9-คำสั่งให้ดำเนินการ-directives)
10. [บทลงโทษและการบังคับใช้](#10-บทลงโทษและการบังคับใช้)

---

## 1. หลักการและเหตุผล

### 1.1 ความเป็นมา

SoloCorp OS 2.0 ดำเนินการด้วย Hermes Agent Profiles จำนวนหลายโปรไฟล์ ซึ่งแต่ละโปรไฟล์แทนบุคลากรในแผนกต่าง ๆ ขององค์กร จาก Org Chart ปัจจุบันมี 9 แผนก:

| แผนก | ชื่อผู้ถือกรรมสิทธิ์ | Role |
|------|-------------------|------|
| CEO | เทอโบ | Chief Executive Officer & Commander |
| CFO | meetoo/หญิง/ค่ะ | Chief Financial Officer |
| CMO | มาร์ค | Chief Marketing Officer |
| Architect | คุณวุฒิ | Solution Architect |
| Orchestrator | พี่ทรงศักดิ์ | Workflow Orchestrator |
| Legal | ตุลย์ | Legal & Governance |
| Design | ครีเอท | Creative Design |
| Engineering | ช่างฟูล | Engineering Lead |
| UI/UX Design | ui-designer | UI/UX Designer |

### 1.2 ปัญหาที่พบ

จากการตรวจสอบสถานะ Hermes Profiles ในระบบ พบประเด็นดังนี้:

1. **Profile `mkt`** — ชื่อไม่สอดคล้องกับ Org Chart ที่ใช้ตำแหน่ง `CMO`
2. **Profile `changful`** — ใช้ชื่อภาษาไทยปนภาษาอังกฤษ แม้จะเข้าใจได้ในบริบท SoloCorp แต่ไม่เป็นมาตรฐานสากล
3. **Profile `arch`** — เป็น directory ว่างเปล่า ไม่มี config.yaml ไม่มีฟังก์ชันใด ๆ (zombie profile)
4. **Profile `default`** — ไม่มี directory หรือ config แยก เป็นเพียง concept ระดับระบบ
5. **ไม่มี Profile สำหรับ `UI/UX Design`** — แผนกที่ 9 ใน Org Chart ยังไม่มี Hermes Profile
6. **ไม่มี Profile `cmo`** — ตำแหน่ง CMO ใช้ชื่อ `mkt` แทน ซึ่งอาจสร้างความสับสน

### 1.3 เหตุผลที่ต้องมีนโยบายนี้

- ป้องกันความสับสนในการอ้างอิงชื่อ profile (โดยเฉพาะเมื่อมีหลายคนติดต่อผ่าน CLI)
- รักษาความเป็นระเบียบของระบบ agent deployment
- สร้างมาตรฐานที่รองรับการขยายตัวของ SoloCorp OS
- ลดความเสี่ยงจาก zombie profile ที่ไม่มีเจ้าของ
- ทำให้การ automate (cron jobs, kanban dispatch, subagent delegation) ทำงานได้อย่างถูกต้อง

---

## 2. ขอบเขตการบังคับใช้

นโยบายนี้ครอบคลุม:

1. **Hermes Agent Profiles** ทั้งหมดที่อยู่ภายใต้ `~/.hermes/profiles/`
2. **Profile Aliases** ที่ใช้ในระบบ SoloCorp OS
3. **Cross-profile references** ใน cron jobs, kanban dispatch, และ subagent delegation
4. **Profile metadata** (description, SOUL.md, references, skills)

**ยกเว้น:**
- Default profile (main `config.yaml`) ไม่ต้องมี directory แยก เนื่องจากเป็นระบบ level
- Session-specific profiles ที่ถูกสร้างแบบชั่วคราวโดย orchestrator

---

## 3. Naming Standard (มาตรฐานการตั้งชื่อ Profile)

### 3.1 กฎบังคับ (Mandatory Rules)

| # | กฎ | รายละเอียด | ตัวอย่าง |
|---|-----|-----------|---------|
| R1 | **Lowercase เท่านั้น** | ชื่อ profile ต้องเป็น lowercase English ทั้งหมด | ✅ `ceo`, `cfo`, `cmo` ❌ `CEO`, `Cmo` |
| R2 | **ห้ามใช้ภาษาไทย** | ห้ามใช้ตัวอักษรไทย เว้นแต่ได้รับ waiver เป็นลายลักษณ์อักษรจาก CEO | ✅ `changful` ❌ ~~ห้าม~~ (อยู่ระหว่าง grandfathered) |
| R3 | **kebab-case สำหรับ 2 คำขึ้นไป** | ถ้าชื่อมีหลายคำ ให้ใช้ hyphen (-) คั่น | ✅ `ui-designer`, `data-analyst` ❌ `ui_designer`, `uiDesigner` |
| R4 | **ห้ามย่อ/ abbreviations เว้นแต่เป็นมาตรฐานสากล** | ใช้ชื่อเต็มของตำแหน่ง ยกเว้นชื่อย่อที่เป็นมาตรฐานสากล (CEO, CFO, CMO, CTO, COO, VP, SVP) | ✅ `cmo` ❌ `mkt` (marketing ไม่ใช่ standard abbreviation) |
| R5 | **ห้ามซ้ำซ้อน** | ห้ามมี 2 profiles ที่ชื่อคล้ายกันจนสับสน | ✅ `architect` ❌ ~~`arch`~~ (ซ้ำซ้อนกับ `architect`) |
| R6 | **ความยาว 2-32 ตัวอักษร** | ชื่อ profile ต้องมีความยาวระหว่าง 2-32 ตัวอักษร | ✅ `ceo` (3), `orchestrator` (12) ❌ `a` (1), `super-long-name-that-exceeds-thirty-two-chars` |
| R7 | **เฉพาะ a-z, 0-9, hyphen (-)** | ไม่อนุญาต character พิเศษอื่น ๆ เช่น underscore, space, dot | ✅ `ui-designer` ❌ `ui.designer`, `ui_designer`, `ui designer` |
| R8 | **ชื่อต้องตรงกับ Org Chart Position** | Profile name ต้องสามารถ map ไปยังตำแหน่งใน SoloCorp Org Chart ได้โดยตรง หรือมี documented alias | ✅ `cfo` → CFO ❌ `mkt` → ??? (ควรเป็น CMO) |

### 3.2 กฎแนะนำ (Recommended Rules)

| # | กฎ | รายละเอียด |
|---|-----|-----------|
| S1 | ใช้ชื่อตำแหน่งงานตาม Org Chart | Map 1:1 กับตำแหน่งใน org chart |
| S2 | หลีกเลี่ยงชื่อเล่น | ยกเว้นกรณีที่ชื่อเล่นเป็นที่รู้จักในบริษัทมากกว่าชื่อตำแหน่ง (เช่น `changful`) |
| S3 | ใช้ภาษาอังกฤษเท่านั้น | เพื่อ interoperability กับเครื่องมือต่างประเทศ |
| S4 | ไม่ใช้หมายเลขหรือรุ่น | เช่น `ceo-v2`, `cfo-prod` |

### 3.3 Reserved Names

ชื่อต่อไปนี้ **ห้ามใช้** เป็น profile name:

- `default` — reserved สำหรับระบบ
- `root` — reserved สำหรับ system-level
- `admin` — reserved
- `system` — reserved
- `hermes` — reserved
- `null`, `none`, `nil` — reserved

---

## 4. SoloCorp Profile Charter

### 4.1 เอกสารบังคับสำหรับทุก Profile

ทุก Profile ที่ใช้งานจริง **ต้องมี** เอกสารดังต่อไปนี้:

| เอกสาร | Path | รายละเอียด | บังคับ |
|--------|------|-----------|:----:|
| `config.yaml` | `~/.hermes/profiles/<name>/config.yaml` | การตั้งค่า model, agent, terminal | ✅ |
| `profile.yaml` | `~/.hermes/profiles/<name>/profile.yaml` | Metadata คำอธิบาย profile (description, tags) | ✅ |
| `SOUL.md` | `~/.hermes/profiles/<name>/SOUL.md` | Personality, tone, เอกลักษณ์ของ profile | ✅ |

### 4.2 ข้อกำหนดของ profile.yaml

```yaml
description: "<string> — คำอธิบายสั้น ๆ ของ profile (สูงสุด 200 ตัวอักษร)"
description_auto: false  # ต้องเป็น false เสมอ (ห้าม auto-generate)
tags:                    # OPTIONAL — tags สำหรับการค้นหา
  - solocorp
  - <department>
aliases:                 # OPTIONAL — alias names ที่ยอมรับได้
  - <alias1>
owner: "<name>"          # ชื่อผู้รับผิดชอบ profile นี้
org_chart_position: "<position>"  # ตำแหน่งใน Org Chart
```

### 4.3 ข้อกำหนดของ SOUL.md

SOUL.md ต้องมีโครงสร้างอย่างน้อย:
- **Identity** — บุคลิกของ agent
- **Expertise** — ความเชี่ยวชาญ
- **Communication Style** — รูปแบบการสื่อสาร
- **Decision Authority** — อำนาจในการตัดสินใจ

### 4.4 ข้อห้าม (Prohibitions)

1. **ห้ามมี profile โดยไม่มี config.yaml** — zombie profiles ต้องถูกลบ
2. **ห้ามมี config.yaml โดยไม่มี SOUL.md** — profile ที่ไม่มีตัวตนไม่สามารถทำงานได้อย่างมีประสิทธิภาพ
3. **ห้ามใช้ `description_auto: true`** — คำอธิบายต้องถูกกำหนดโดยมนุษย์
4. **ห้ามแก้ไข profile ของแผนกอื่น** โดยไม่ได้รับอนุญาตเป็นลายลักษณ์อักษร

---

## 5. Accountability & Ownership

### 5.1 Profile Owner Registry

**Profile Registry Master** ถูกจัดเก็บที่:
- `~/.hermes/memories/MEMORY.md` — ต้องมี section "SoloCorp Profile Registry"
- และ/หรือที่ `~/SoloCorp_Profile_Registry.yaml`

### 5.2 ตารางความรับผิดชอบ

| Profile | Owner (Role) | Department | รับผิดชอบโดย |
|---------|-------------|-----------|-------------|
| `ceo` | CEO (หนุมาน) | Executive | CEO เอง |
| `cfo` | CFO (meetoo) | Finance | CFO |
| `cmo` (ปัจจุบันคือ `mkt`) | CMO (มาร์ค) | Marketing | CMO (ต้อง rename ก่อน) |
| `architect` | Arch (คุณวุฒิ) | Architecture | คุณวุฒิ |
| `orchestrator` | Orch (พี่ทรงศักดิ์) | Orchestration | พี่ทรงศักดิ์ |
| `legal` | Legal (ตุลย์) | Legal & Governance | ตุลย์ |
| `design` | Design (ครีเอท) | Creative | ครีเอท |
| `changful` | Engineering (ช่างฟูล) | Engineering | ช่างฟูล |
| `ui-designer` | UI/UX Design | UI/UX Design | **ต้องสร้างใหม่** |

### 5.3 หน้าที่ของ Profile Owner

1. **ดูแลรักษา** config.yaml, profile.yaml, SOUL.md ให้เป็นปัจจุบัน
2. **ตรวจสอบ** logs และ errors ของ profile ของตน (อย่างน้อยสัปดาห์ละครั้ง)
3. **ตอบสนอง** ต่อ Security/Compliance alerts ที่เกี่ยวกับ profile ของตน
4. **อนุมัติ** การเปลี่ยนแปลงใด ๆ ต่อ profile ของตน
5. **รายงาน** การละเมิดนโยบายไปยัง Legal (คุณตุลย์)

### 5.4 Legal (คุณตุลย์) ในฐานะ Governance Authority

- **Audit ทุก 90 วัน** — ตรวจสอบ compliance ของทุก profile
- **รักษา Registry** — ดูแล Profile Registry Master ให้เป็นปัจจุบัน
- **ให้ waiver** — ในกรณีจำเป็น สามารถให้ข้อยกเว้นได้ (ต้องได้รับอนุมัติจาก CEO)
- **บังคับใช้นโยบาย** — ดำเนินการตามบทลงโทษเมื่อมีการละเมิด

---

## 6. Resolution Protocol (เมื่อเกิด Conflict)

### 6.1 ประเภทของ Conflict

| Type | คำอธิบาย | ตัวอย่าง |
|------|---------|---------|
| **T1 — Naming Conflict** | ชื่อ profile ซ้ำหรือใกล้เคียงกัน | `architect` vs `arch` |
| **T2 — Ownership Conflict** | Profile เดียวกันมีเจ้าของ 2 คน | — |
| **T3 — Scope Conflict** | ขอบเขตงานของ profile ทับซ้อนกัน | `design` vs `ui-designer` |
| **T4 — Zombie Profile** | Profile ที่ไม่มี config.yaml หรือไม่มี owner | `arch` |
| **T5 — Orphan Profile** | Owner ลาออกหรือไม่มีการดูแล | — |

### 6.2 ขั้นตอนการแก้ไข

#### T1 — Naming Conflict Resolution

1. **รายงาน** — ผู้พบ conflict รายงานไปยัง Legal (คุณตุลย์)
2. **วิเคราะห์** — Legal ตรวจสอบประวัติและความจำเป็นของชื่อแต่ละชื่อ
3. **ตัดสิน** — ใช้กฎ Naming Standard ข้อ R4 และ R5:
   - ชื่อที่ถูกต้องตามมาตรฐานจะคงอยู่
   - ชื่อที่ไม่ถูกต้องต้องถูก rename ภายใน 7 วัน
4. **กรณีพิเศษ** — ถ้าทั้งสองชื่อถูกต้องตามมาตรฐาน ให้ใช้หลัก "first-come-first-served" เว้นแต่ CEO จะสั่งเป็นอย่างอื่น

#### T3 — Scope Conflict Resolution

1. **ประชุม** — Owner ของ profiles ที่เกี่ยวข้องประชุมร่วมกับ Legal
2. **ดีลิเนียต** — เขียน Role Boundary Document (RBD) แยกขอบเขต
3. **ลงนาม** — RBD ต้องได้รับการอนุมัติจาก CEO

#### T4 — Zombie Profile Resolution

1. **ตรวจพบ** — โดย Legal audit หรือ automated scan
2. **แจ้งเตือน** — ประกาศให้owner ทราบ (ถ้ามี) + แจ้ง CEO
3. **รอ 14 วัน** — ถ้าไม่มีการเคลม หรือไม่มีการใส่ config ให้ดำเนินการลบ
4. **ลบ** — ลบ directory ทิ้ง หรือ archive ไปยัง `~/.hermes/profiles/_archived/`

#### T5 — Orphan Profile Resolution

1. **ตรวจพบ** — โดย Legal audit
2. **หา owner ใหม่** — CEO หรือ Head of Department ที่เกี่ยวข้อง
3. **Transfer** — เปลี่ยน owner metadata ใน profile.yaml
4. **ลบ** — ถ้าไม่มี owner ภายใน 30 วัน ดำเนินการตาม T4

---

## 7. Change Management (การ Rename/เพิ่ม/ลบ Profile)

### 7.1 ระดับการเปลี่ยนแปลง

| Level | คำอธิบาย | ต้องขออนุมัติจาก | เวลาดำเนินการ |
|-------|---------|---------------|:-----------:|
| L1 — Minor | แก้ไข description, tags | Owner อนุมัติเองได้ | ทันที |
| L2 — Standard | เพิ่ม/ลบ skills, references, SOUL.md | Owner + Department Head | ภายใน 3 วัน |
| L3 — Major | **Rename profile**, เพิ่ม profile ใหม่ | Owner + Legal + CEO | ภายใน 7 วัน |
| L4 — Critical | ลบ profile ทิ้ง | Legal + CEO | ภายใน 14 วัน |

### 7.2 กระบวนการ Rename Profile (L3 — Major Change)

**Step 1: ยื่นคำขอ**
- Owner ยื่น Change Request ไปยัง Legal (คุณตุลย์)
- ในคำขอต้องระบุ: ชื่อเดิม, ชื่อใหม่, เหตุผล, แผนก, ผลกระทบ

**Step 2: Legal Review**
- ตรวจสอบชื่อใหม่ว่า compliance กับ Naming Standard หรือไม่
- ตรวจสอบว่าไม่มี name conflict
- ตรวจสอบผลกระทบต่อ cron jobs, kanban dispatch, cross-profile references

**Step 3: CEO Approval**
- CEO อนุมัติ หรือ ปฏิเสธ พร้อมเหตุผล

**Step 4: Execute**
เมื่อได้รับอนุมัติ:
1. สร้าง profile ใหม่พร้อมชื่อใหม่ (copy config.yaml, SOUL.md, references)
2. อัปเดต profile registry
3. แจ้ง团队成员 ที่เกี่ยวข้อง (Engineering, Orch)
4. รักษา profile เดิมไว้ 30 วัน (grace period) พร้อม symlink/logic fallback
5. หลังจาก 30 วัน — ลบ profile เดิม

**Step 5: Documentation**
- อัปเดต SoloCorp Profile Charter
- อัปเดตเอกสารอ้างอิงทั้งหมด

### 7.3 กระบวนการเพิ่ม Profile ใหม่ (L3 — Major Change)

1. **ยื่นคำขอ** — Owner หรือ Department Head ยื่นไปยัง Legal + CEO
2. **ตรวจสอบ** — Legal ตรวจสอบชื่อ, ขอบเขต, และผลกระทบ
3. **CEO อนุมัติ**
4. **สร้าง** — สร้าง directory structure:
   ```
   profiles/<name>/
   ├── config.yaml
   ├── profile.yaml
   ├── SOUL.md
   ├── references/
   └── logs/
   ```
5. **Register** — Legal อัปเดต Profile Registry
6. **ประกาศ** — แจ้งทุกแผนกผ่านช่องทางที่กำหนด

### 7.4 กระบวนการลบ Profile (L4 — Critical Change)

1. **ตรวจสอบ dependencies** — cron jobs, kanban queues, other profile references
2. **Migrate** — ย้าย dependencies ไปยัง profile อื่นหรือลบทิ้ง
3. **Archive** — ย้ายไปยัง `~/.hermes/profiles/_archived/<name>/`
4. **Registry** — Legal อัปเดต Profile Registry
5. **รอ 90 วัน** — ถึงจะลบถาวร

---

## 8. การวิเคราะห์ Compliance ของ Profiles ปัจจุบัน

### 8.1 Compliance Matrix

| Profile | Naming OK? | Has config? | Has profile.yaml? | Has SOUL.md? | Owner assigned? | Org Chart Match? | สถานะ |
|---------|:---------:|:----------:|:----------------:|:-----------:|:--------------:|:---------------:|:-----:|
| `ceo` | ✅ | ✅ | ✅ | ✅ | ✅ CEO (หนุมาน) | ✅ CEO | **COMPLIANT** |
| `cfo` | ✅ | ✅ | ✅ | ✅ | ✅ CFO (meetoo) | ✅ CFO | **COMPLIANT** |
| `mkt` | ❌ | ✅ | ❌ | ❌ | ❓ CMO (มาร์ค) | ❌ แผนก CMO | **NON-COMPLIANT** |
| `architect` | ✅ | ✅ | ❌ | ❌ | ❓ Arch (คุณวุฒิ) | ✅ Architect | **PARTIALLY COMPLIANT** |
| `orchestrator` | ✅ | ✅ | ❌ | ❌ | ❓ Orch (พี่ทรงศักดิ์) | ✅ Orchestrator | **PARTIALLY COMPLIANT** |
| `legal` | ✅ | ✅ | ✅ | ✅ | ✅ Legal (ตุลย์) | ✅ Legal | **COMPLIANT** |
| `design` | ✅ | ✅ | ❌ | ❌ | ❓ Design (ครีเอท) | ✅ Design | **PARTIALLY COMPLIANT** |
| `changful` | ⚠️ | ✅ | ❌ | ❌ | ❓ Eng (ช่างฟูล) | ✅ Engineering | **PARTIALLY COMPLIANT** |
| `arch` | ❌ | ❌ | ❌ | ❌ | ❌ ไม่มี | ❌ Duplicate | **ZOMBIE — ต้องลบ** |
| `ui-designer` | ❌ | ❌ | ❌ | ❌ | ❌ ไม่มี | ❌ แผนก UI/UX | **MISSING — ต้องสร้าง** |

### 8.2 การวิเคราะห์เฉพาะ `mkt` Profile

**ประเด็น:** Profile `mkt` ใช้ชื่อย่อ "mkt" แทน "cmo" ซึ่งขัดต่อ:

1. **Naming Standard R4:** "ห้ามย่อ/abbreviations เว้นแต่เป็นมาตรฐานสากล" — `mkt` ไม่ใช่ abbreviation มาตรฐานสากล (ต่างจาก CEO, CFO, CMO)
2. **Naming Standard R8:** "ชื่อต้องตรงกับ Org Chart Position" — Org Chart ไม่มีตำแหน่ง "Marketing" มีแต่ "CMO"
3. **Org Chart Alignment:** แผนก Marketing ใน SoloCorp คือ CMO (มาร์ค) ไม่ใช่ MKT

**คำวินิจฉัยทางกฎหมาย:** Profile `mkt` **ผิดกฎ Naming Standard** และต้องถูก rename เป็น `cmo` ภายใน 7 วัน ตามกระบวนการ L3 Change Management

**ข้อยกเว้น (Waiver) ที่พิจารณาแล้ว:** ไม่สมควรให้ waiver เนื่องจาก:
- `cmo` เป็นชื่อที่สั้นกว่าและเป็นมาตรฐานสากล
- ไม่มีค่าใช้จ่ายหรือ downtime ในการ rename
- การคงชื่อ `mkt` ไว้จะสร้าง precedence ที่ไม่ดีสำหรับ profile อื่นในอนาคต

### 8.3 การวิเคราะห์เฉพาะ `changful` Profile

**ประเด็น:** Profile `changful` ใช้ชื่อภาษาไทย (ช่างฟูล) ปนกับอังกฤษ

**การวิเคราะห์:**
1. **Naming Standard R2:** "ห้ามใช้ภาษาไทย เว้นแต่ได้รับ waiver"
2. **ข้อเท็จจริง:** "changful" เป็นการทับศัพท์ภาษาไทย (ช่างฟูล) ด้วยอักษรโรมัน — **ไม่ใช่ภาษาไทยโดยตรง**
3. **Business Context:** "ช่างฟูล" เป็นชื่อเล่นที่团队成员ใช้กันทั่วไปใน SoloCorp การเปลี่ยนชื่ออาจสร้างความสับสนในทีม
4. **Org Chart Match:** แผนก Engineering (ช่างฟูล) — ชื่อ profile `changful` สามารถ map ไปยังตำแหน่ง Engineering Lead ได้

**คำวินิจฉัยทางกฎหมาย:** Profile `changful` **สามารถ grandfathered (ได้รับการยกเว้น)** ภายใต้เงื่อนไข:
1. เพิ่ม `profile.yaml` ที่ระบุ `org_chart_position: "Engineering"` และ `aliases: ["engineering"]`
2. สร้าง symlink หรือ documented alias `engineering` → `changful` 
3. profile ใหม่ทั้งหมดหลังจากวันนี้ **ห้าม** ใช้รูปแบบนี้

**เหตุผล:** ชื่อ `changful` สร้าง brand identity และ recognition ภายในทีม SoloCorp แล้ว และการเปลี่ยนชื่อเป็น `engineering` อาจสร้างความสับสนมากกว่าประโยชน์

---

## 9. คำสั่งให้ดำเนินการ (Directives)

### 9.1 Immediate Actions (ภายใน 7 วัน)

| # | Action | Owner | Deadline | Status |
|---|--------|-------|:--------:|--------|
| D1 | **Rename `mkt` → `cmo`** | Legal + CMO (มาร์ค) | 7 วัน | ✅ **COMPLETED** 2026-06-22 — profile สร้างแล้ว, `mkt` กลายเป็น symlink → `cmo` |
| D2 | **ลบ zombie profile `arch`** | Legal | 7 วัน | ✅ **COMPLETED** 2026-06-22 — directory ย้ายไป `~/.hermes/trash/` |
| D3 | **สร้าง `ui-designer` profile** | Legal + UI/UX Design | 7 วัน | ✅ **COMPLETED** 2026-06-22 — profile + SOUL.md สร้างแล้ว |

### 9.2 Short-term Actions (ภายใน 30 วัน)

| # | Action | Owner | Deadline | Status |
|---|--------|-------|:--------:|--------|
| D4 | สร้าง `profile.yaml` สำหรับ profiles ที่ขาด | Profile Owner แต่ละคน | 30 วัน | ⏳ Pending |
| D5 | สร้าง `SOUL.md` สำหรับ profiles ที่ขาด | Profile Owner แต่ละคน | 30 วัน | ⏳ Pending |
| D6 | อัปเดต Profile Registry ใน `MEMORY.md` | Legal | 30 วัน | ✅ **COMPLETED** 2026-06-22 |
| D7 | สร้าง `engineering` profile + symlink alias `changful→engineering` | Engineering (ช่างฟูล) | 30 วัน | ✅ **COMPLETED** 2026-06-22 — profile สร้างแล้ว, `changful` กลายเป็น symlink → `engineering` |

### 9.3 Long-term Actions (ภายใน 90 วัน)

| # | Action | Owner | Deadline |
|---|--------|-------|:--------:|
| D8 | Compliance Audit ครั้งแรก | Legal | 90 วัน |
| D9 | ทบทวนนโยบาย Governance Policy ครั้งแรก | Legal | 90 วัน |
| D10 | สร้าง automated profile compliance checker script | Engineering | 90 วัน |

---

## 10. บทลงโทษและการบังคับใช้

### 10.1 การละเมิดนโยบาย

| ระดับ | คำอธิบาย | ผล |
|:----:|---------|-----|
| **Level 1 — Minor** | ไม่มี profile.yaml หรือ SOUL.md | หนังสือเตือน + ให้เวลา 30 วันแก้ไข |
| **Level 2 — Moderate** | ใช้ชื่อผิดกฎ Naming Standard | ต้อง rename ภายใน 7 วัน |
| **Level 3 — Severe** | สร้าง zombie profile, duplicate profile | ต้องลบภายใน 14 วัน + รายงาน CEO |
| **Level 4 — Critical** | การละเมิดที่ส่งผลต่อระบบ production | ปลด profile ออกจากการใช้งานทันที + สอบสวน |

### 10.2 การบังคับใช้

- Legal (คุณตุลย์) มีอำนาจในการ **ระงับการใช้งาน profile** ชั่วคราว หากพบว่ามีการละเมิด Level 3 ขึ้นไป
- การระงับสามารถทำได้โดยการ เพิ่ม `disabled: true` หรือ `hidden: true` ใน config.yaml
- Profile owner ที่ถูกระงับสามารถยื่นอุทธรณ์ต่อ CEO ได้ภายใน 14 วัน

### 10.3 ข้อยกเว้น (Waiver)

- CEO สามารถให้ waiver สำหรับกรณีพิเศษได้
- Waiver ทั้งหมดต้องเป็นลายลักษณ์อักษรและถูกจัดเก็บใน `~/.hermes/profiles/_governance/waivers/`
- Waiver มีอายุสูงสุด 180 วัน และต้องได้รับการต่ออายุ

---

## ภาคผนวก

### A. Profile Registry Template

```yaml
# SoloCorp Profile Registry
# จัดทำโดย: Legal (คุณตุลย์)
# อัปเดตล่าสุด: 2026-06-22

profiles:
  - name: ceo
    status: active
    owner: "CEO (หนุมาน)"
    department: Executive
    org_chart_position: CEO
    created: "2026-01-01"
    compliance: compliant

  - name: cfo
    status: active
    owner: "CFO (meetoo)"
    department: Finance
    org_chart_position: CFO
    created: "2026-01-01"
    compliance: compliant

  - name: cmo
    status: pending_rename_from_mkt
    owner: "CMO (มาร์ค)"
    department: Marketing
    org_chart_position: CMO
    created: "2026-01-01 (as mkt)"
    compliance: non_compliant
    action: "ต้อง rename จาก mkt ภายใน 2026-06-29"
```

### B. Change Request Form

```
เรื่อง: ขอเปลี่ยนแปลง Profile
ชื่อเดิม: ___________
ชื่อใหม่: ___________
ประเภท: [Rename / Create / Delete / Modify]
เหตุผล: _____________________________________________
แผนกที่รับผิดชอบ: ____________________________________
Owner: _____________________________________________
ผลกระทบที่คาดว่าจะเกิด: ________________________________
วันที่ยื่นคำขอ: ________________________________________
ลงชื่อ (Owner): _______________________________________
ลงชื่อ (Legal): ________________________________________
ลงชื่อ (CEO): _________________________________________
```

### C. Role Boundary Document Template (สำหรับ T3 — Scope Conflict)

```
Role Boundary Document
Profile A: ___________
Profile B: ___________
วันที่: _______________

1. ขอบเขตเฉพาะของ Profile A:
   - 
2. ขอบเขตเฉพาะของ Profile B:
   -
3. ขอบเขตที่ทับซ้อนกัน (ต้องทำงานร่วมกัน):
   -
4.  escalation path เมื่อ scope conflict:
   -
5. วันที่เริ่มมีผล: _______________
6. วันที่ทบทวนครั้งต่อไป: _______________
ลงชื่อ (Owner A): ___________  ลงชื่อ (Owner B): ___________
ลงชื่อ (Legal): _____________  ลงชื่อ (CEO): ______________
```

---

> **เอกสารนี้เป็นนโยบายอย่างเป็นทางการของ SoloCorp OS**
> **ผู้ละเมิดนโยบายอาจถูกดำเนินการทางวินัยตามข้อ 10**
>
> — Legal (คุณตุลย์), SoloCorp OS Governance
