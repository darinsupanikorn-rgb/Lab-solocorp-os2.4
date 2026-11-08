# ADR-029: ความขัดแย้งของตรรกะใน `rules/` + `sop/` — 12 จุด หนึ่งเรื่องต้องมีหนึ่งมาตรฐาน

**วันที่:** 2026-10-25
**สถานะ:** Proposed ⏳ — รอ Owner (L5 บางข้อ) / CEO (L4) ตัดสินใจ
**Owner:** CEO หนุมาน (รวบรวม) → Dr.solodev (ตัดสินข้อที่แตะ org structure + quality baseline)
**ที่มา:** Owner รายงานว่า "logic เดิมขัดแย้งกันจนไม่รู้จะเริ่มต่อยังไง" (25 ต.ค. 2569) — ทวนอ่าน `rules/01–06` + `sop/SOP-01–07` ทั้งหมดแล้วพบ 12 จุดที่สองฉบับ (หรือสองไฟล์) สั่งสิ่งต่างกันในเรื่องเดียว
**เกี่ยวกับ:** ADR-016 (behavior-centric routing) · ADR-017 (@mention gate) · ADR-028 (mirror scoring แยกตามระดับ)

---

## บริบท

`rules/` (6 ไฟล์) กับ `sop/` (7 ไฟล์) ถูกเขียน/แก้คนละช่วงเวลา (ก.ค. → ต.ค. 69) โดยไม่มีขั้นตอนตรวจความสอดคล้องระหว่างกัน ผลคือ **เรื่องเดียวมี 2–3 คำตอบ** เมื่อ agent เจอแบบนี้จะเลือกตามใจสะดวก หรือ worst case = confabulate (แบบ incident @changful 05 ส.ค.)

**หลักการแก้ที่ใช้ทั้ง ADR (rank อำนาจ — เวลาขัดกัน ใครจริงกว่า):**

1. **สิ่งที่รันได้จริง (โค้ด / CI / ค่าในไฟล์ config) = ข้อเท็จจริง** — `rules`/`sop` ห้ามเขียนเกินกว่านั้น除非แก้โค้ดพร้อมกันใน changeset เดียว
2. **ADR ใหม่สุด > SOP > rules > command template (`opencode.json`, `.claude/settings.json`) > profile/memory**
3. **กฎที่ไม่มีจุดตรวจ (checkbox) ใน checklist ของขั้นตอน = ไม่มีผลบังคับ** — เขียนอย่างเดียวไม่พอ
4. **หนึ่งเรื่อง = หนึ่งชุดคำศัพท์** — ถ้าโค้ดใช้ `high/normal/low` docs ต้องใช้ชุดเดียวกัน หรือมีตารางแปลงหน้าเดียวชัดเจน

---

## ตารางสรุป 12 จุด

| # | เรื่อง | ฝั่ง A | ฝั่ง B | ผลกระทบ | เสนอแก้ | ระดับ |
|:-:|:-------|:-------|:-------|:--------|:--------|:-----:|
| **X1** | COO มีหรือไม่มี | `profiles/INDEX.md` + `AGENTS.md` + `workers/agents/coo_dispatch_agent.py` = COO (กิจ) เป็น L1–L3 gatekeeper | `rules/02-work.md` hierarchy และ `rules/01-receive.md` §3 ไม่มี COO เลย · `sop/SOP-02` L3 → Head ตัดสินตรง | ใครคุม daily ops/L1–L3 มี 3 คำตอบ · route table ไม่รู้จักแผนกที่มีโค้ดจริง | ใส่ COO เข้า hierarchy + route table + escalation flow ให้ตรง AGENTS.md (มีโปรไฟล์+โค้ดแล้ว) — หรือถ้าไม่เอา COO ให้ลบโปรไฟล์+โค้ดทิ้ง | **L5** |
| **X2** | จำนวนแผนก 19 vs 20 | `rules/05-env.md:38` "19 department SOUL.md" · `rules/02-work.md` นับ 19 · `brain/*` บอก 19 | `profiles/` มี **20 โฟลเดอร์** (รวม `02-coo`) · ADR-028 เขียน "12/20 แผนก" | ตัวเลขใน rules ผิด → การนับ head/route/coverage ของ org ผิดไปด้วย | ให้ `profiles/INDEX.md` เป็น sole source — `rules/05` เขียน "N แผนก (ตาม INDEX.md)" ไม่เขียนตัวเลขตายตัว | L4 |
| **X3** | 4 ชุดคำศัพท์ ไม่มีตารางแปลง | `rules/01` §1 = **P0–P3** · `SOP-03` handoff = **P0–P3** | `rules/01` §2 + `SOP-02` = **L1–L5** · `SOP-05` = **CRIT/HIGH/MED/LOW** · `SOP-01` + โค้ด = **high/normal/low** (`central_bus/webhook_receiver.py:78`, `workers/agents/base_agent.py:227`) | "ระบบล่ม (P0)" ควรปฏิบัติยังไงไม่มีคำตอบ: `SOP-05` สั่งแจ้ง Owner ทันที แต่ `SOP-02` บอกส่ง L1–L4 ถึง Owner = **system failure** | ประกาศชัดว่า 3 scale คนละแกน: Severity (SOP-05) / Decision level (L1–L5) / Queue weight (high/normal/low) + ตาราง map หน้าเดียวใน `rules/01` §1 · แก้ตัวอย่าง handoff `"priority": "high"` ใน `rules/01` §4 ให้ตรง enum ของ `SOP-03` | L4 |
| **X4** | Coverage: สองเกณฑ์บอกผลคนละแบบกับเลขเดียวกัน | `sop/SOP-04` QA gate: **APPROVED ≥80% · CONDITIONAL 70–79% · block <70%** (`workers/qa_signoff_gate.py:15`) | CI: `auto_qa_gate --threshold=9` · `.coveragerc` `fail_under = 0` · `AGENTS.md` บอก baseline 9 ตั้งใจ ห้ามยกโดยไม่มี ADR | **ผลรันจริง 25 ต.ค.: coverage 75.3%, 948 tests ผ่าน** → CI 🟢 PASS สบายๆ แต่ `qa_signoff_gate` ให้ได้แค่ **CONDITIONAL** (70–79% = ต้องมีเอกสารเงื่อนไข+timeline ทุกครั้ง) → สอง gate ขัดผลกันด้วยเลขเดียวกัน | **ต้องเลือก 1:** (ก) ปรับ `qa_signoff_gate` ให้รับ threshold จาก config เดียวกับ CI แล้วยกเป็นลำดับ (ขัด AGENTS.md → ต้องมี ADR นี้แหละ) · (ข) ประกาศว่า `qa_signoff_gate` ใช้เฉพาะ feature ที่ตั้ง target coverage แล้วเท่านั้น ไม่ใช่ทุก deploy | **L5** |
| **X5** | `/deploy` command ข้ามขั้นตอนบังคับ | `opencode.json:227` + `.claude/settings.json:60`: ขั้นตอน 1–5 = build → export → verify → commit → report (**ไม่มีรัน test, ไม่มี QA sign-off**) | `sop/SOP-04` v2.0: "**No QA sign-off = No deploy**" + step 1 pre-deploy test | ทางการของ CLI ละเมิด SOP ทุกครั้งที่ใช้ `/deploy` | แก้ template ทั้ง 2 ไฟล์ให้เหลือ "ทำตาม SOP-04 ทุกขั้น (test → QA gate → build → validate → commit → report)" — กัน drift ซ้ำเพราะมี 2 จุด | L4 |
| **X6** | Route table สั่ง `@mention` แต่ §4 ห้าม (ไฟล์เดียวกัน) | `rules/01-receive.md:50` — "code, implement → `@changful`" | `rules/01-receive.md:109` — "`@mention` dept agent ตรงๆ → ❌ ห้ามชั่วคราว" (ADR-017) | ทุกการ route ตาม §3 = ละเมิด §4 → เสียรอบฟรีจาก free-tier gate | เพิ่มคอลัมน์ "เรียกยังไง (ช่วง ADR-017)" ใน §3 ทุกแถว = `/workspace [dept] [task]` จนกว่า upstream จะคืนสภาพ | L4 |
| **X7** | "Head ห้าม implement" vs route ส่งงานตรงถึง Head | `rules/01:116` + `rules/04` §1: ❌ Head ลงมือ implement เอง — delegate เสมอ | `rules/01:50` route งาน code ตรงถึงหัวหน้า `@changful` · `sop/SOP-04` Owner = Engineering ทำ build/validate/commit เอง | ไม่ชัดว่า Head = ผู้รับงาน หรือ ผู้ส่งต่อ → certification D-level ของใครไม่รู้ | ประกาศ: **Head = outcome owner รับ request แล้วส่งต่อ specialist ผ่าน Bus เสมอ** + อนุญาตข้อยกเว้นเมื่อ specialist ไม่มีเครื่องมือ โดย **ต้องจดข้อยกเว้น** (มี precedent แล้ว: `brain/learnt.md:199`) | L4 |
| **X8** | Certification gate ไม่มีใน checklist ของขั้นตอน | `rules/06-certification.md` §6: "ก่อน dispatch งาน execution → เช็ค registry D2+ · D0 ห้ามรับงาน" | `sop/SOP-01` checklist 6 ข้อ **ไม่มี**ข้อเช็ค D2+ · `sop/SOP-06` checklist ก็ไม่มี | กฎมีแต่ขั้นตอนไม่มี → incident แบบ 05 ส.ค. ซ้ำได้ | เพิ่ม checkbox "ผู้รับงานผ่าน D2+ แล้ว? (`profiles/CERTIFICATION-REGISTRY.md`)" ใน `SOP-01` §Checklist และ `SOP-06` §Checklist | L4 |
| **X9** | Mirror Check มี 3 ชุดเกณฑ์ | `rules/01` §2: system auto สำหรับ L3+ · manual 3 คำถามเป็น backup | `sop/SOP-01` step 1: "ต้องผ่าน Mirror Check (**3 คำถาม**) ก่อน" · **ADR-028**: เกณฑ์จริง = score ≥60% ของชุดคำถามตามระดับใน `central_bus/mirror_check.py` + L1/L2 = advisory ไม่ block | ไม่รู้ว่า "ผ่าน" หมายถึงอะไร — 3 ข้อ manual หรือ score 60%? · `SOP-01` ไม่รู้จัก ADR-028 เลย | ให้ `central_bus/mirror_check.py` เป็น single source · `SOP-01` เขียน "ผ่าน mirror gate ตาม ADR-028" · manual 3 คำถาม = fallback เมื่อ busd ไม่ทำงาน (ต้องประกาศชัดว่า fallback) | L4 |
| **X10** | ช่องทางถึง Owner | `rules/02-work.md:30` — "Owner คุยกับ **CEO เท่านั้น**" | `sop/SOP-05` — CRIT "✅ แจ้ง Owner ทันที" + post-mortem "Owner รับทราบ (L5)" · `rules/06` D1/D4 ผู้ตรวจ = Owner โดยตรง | agent ไม่รู้ว่าแจ้งตรงได้ไหม → เลือกเงียบ (อันตรายกับ CRIT) | แยก 2 กรณีใน `SOP-02`: งานประจำ/decision → ผ่าน CEO เท่านั้น · **เหตุฉุกเฉิน (CRIT) + บทบาทผู้ตรวจ → แจ้งตรงได้** | L4 |
| **X11** | สั่งใช้เครื่องมือที่ไม่มีอยู่จริง | `rules/03-session.md:24-27` สั่ง `deja "คำค้น"` / `deja show/resume/stats` และ "**ก่อนไล่บั๊ก → deja ก่อน**" | `command -v deja` → **ไม่มีในเครื่อง** | rule บังคับขั้นตอนที่รันไม่ได้ = ชวนให้ข้ามเงียบๆ หรือรายงานเท็จ | ติดตั้ง `deja` ให้ได้ หรือแทนด้วย `rg` + `brain/session-log.md` — ถ้ายังไม่มีให้ติดป้าย "ต้องติดตั้งก่อนใช้" | L3 |
| **X12** | Handoff payload 2 ชุด | `rules/01` §4 JSON: `status: "ready"`, `priority: "high"`, ไม่มี acceptance criteria / confirmation record | `sop/SOP-03` v1.1: `priority: P0–P3` + Quality Gate บังคับ acceptance criteria + deadline + **confirmation record ก่อนเริ่มงาน** (`workers/handoff_confirm.py`) | payload ที่สร้างตาม `rules/01` จะถูก `SOP-03` ตีตก และโค้ด confirm 期待 status `acknowledged/need_clarify/rejected` ไม่ใช่ `ready` | ให้ `SOP-03` เป็น truth สำหรับ handoff — `rules/01` §4 เหลือแค่ลิงก์ไป `SOP-03` + คำสั่ง (ลดจุดซ้ำ = กัน drift) | L3 |

---

## ตัดสินใจ (รอการอนุมัติ)

1. **ใช้ rank อำนาจ 4 ข้อด้านบนเป็นกติกาถาวร** ของ repo นี้ — ทุกครั้งที่เขียน rule/SOP ใหม่ ต้องเทียบ rank ก่อน
2. **X1 และ X4 เป็น L5** (org structure + quality baseline) — ต้อง Owner ตัดสิน เพราะแตะสายบังคับบัญชาและเกณฑ์รับงาน
3. **X2, X3, X5, X6, X7, X8, X9, X10 เป็น L4** — CEO ตัดสินแล้วรายงาน
4. **X11, X12 เป็น L3** — Head (หรือผู้รับผิดชอบไฟล์นั้น) แก้ได้เลย
5. **X5 และ X12 แก้ที่ต้นทางเดียว** ไม่ split: `/deploy` template กับ `rules/01` §4 ต้องกลายเป็นลิงก์/คำสั่งสั้นๆ ชี้ไป SOP ห้าม duplicate สูตรไว้อีก

## เหตุผล

1. **ปัญหาไม่ใช่ "กฎน้อยไป" แต่คือ "กฎซ้ำกันแล้วไม่ sync"** — `rules/01` §4 และ `SOP-03` เขียนสูตร handoff เหมือนกัน 2 ชุด ยิ่งซ้ำยิ่งมีโอกาสขัด ทางแก้คือเหลือจุดเดียวแล้วชี้ไป
2. **กฎที่ไม่มี checklist = ไม่มีอยู่จริง** — X8 คือหลักฐาน: เขียน D2+ gate ไว้ใน `rules/06` แต่ `SOP-01` ไม่ถาม → งาน dispatch ไม่เคยถูกกันไว้
3. **ห้ามเขียนเกินกว่าสิ่งที่รันได้** — X4/X11 คือชนวนเดียวกัน: เอกสารสั่งเกินสิ่งที่ระบบมี (threshold 80%, CLI ที่ไม่มี) → ผู้ทำต้องเลือกว่าจะเชื่อเอกสารหรือเชื่อของจริง ซึ่งเป็นจุดที่ทำให้ "รู้ว่าต่อยังไงไม่ได้"
4. **ของจริงที่ดีอยู่แล้วต้องไม่ถูกเขียนทับ** — `AGENTS.md` (ที่ถูก auto-load) มี COO ครบวงจร และ ADR-028 แก้ mirror ไปแล้ว แต่ `rules/` ยังเขียนแบบก่อน ADR-028 → rules คือฝั่งที่ต้องอัปเดต ไม่ใช่กลับไปแก้ของใหม่

## ผลกระทบที่ต้องรู้

1. **แก้ X1/X2 จะกระทบตัวเลขหลายจุด** — route table, hierarchy, `rules/05` key paths, `brain/` ที่เขียน 19 ไว้ (ให้ `profiles/INDEX.md` เป็น sole source จะเลิกต้องไล่แก้ทุกที่)
2. **X4 ถ้าเลือกปรับ threshold ต้องมีการ commit ค่าใหม่ + บอกทีม** — เปลี่ยนเกณฑ์รับงาน = เปลี่ยนคำว่า "ผ่าน"
3. **X6/X7 มีผลเฉพาะช่วง ADR-017** — ต้องมีเงื่อนไข "คืนค่าเมื่อ upstream แก้" ไม่งั้น rule ชั่วคราวจะกลายเป็น rule ถาวร (แบบที่ `rules/01` §4 กำลังเป็น)
4. **ยังไม่ได้แก้ไฟล์ไหนเลย** — ADR นี้คือรายการงาน (backlog) เท่านั้น การแก้ `rules/`/`sop/` ต้องทำทีละข้อตาม rank ที่ตัดสินแล้ว

## งานที่ต้องทำต่อ (ถ้าอนุมัติ)

- [ ] Owner ตัดสิน X1 (COO) และ X4 (coverage baseline)
- [ ] CEO ตัดสิน X2, X3, X5–X10 แล้วแก้ไฟล์ที่เกี่ยว
- [ ] X11: ตรวจว่า `deja` อยู่ใน roadmap หรือลบออกจากระบบความจำ
- [ ] X12: ย่อ `rules/01` §4 เหลือลิงก์ไป `SOP-03`
- [ ] เพิ่มจุดตรวจ "rules/sop สอดคล้องกับโค้ดไหม" เข้า pre-deploy checklist ของ `SOP-04` (กัน drift รอบหน้า)

## References

- `rules/01-receive.md` §1–§5 · `rules/02-work.md` §1–§2 · `rules/03-session.md` §2 · `rules/05-env.md` §4 · `rules/06-certification.md` §6
- `sop/SOP-01-dispatch.md` §Checklist · `sop/SOP-02-escalation.md` · `sop/SOP-03-handoff.md` §Quality Gate · `sop/SOP-04-deploy.md` §QA Sign-off Gate · `sop/SOP-05-incident.md`
- `opencode.json` → `command.deploy` (line 225) · `.claude/settings.json` → `command.deploy` (line 58)
- `workers/qa_signoff_gate.py` · `workers/auto_qa_gate.py` · `workers/handoff_confirm.py` · `workers/agents/coo_dispatch_agent.py` · `central_bus/mirror_check.py`
- `profiles/INDEX.md` · `profiles/02-coo/SOUL.md` · `AGENTS.md` · `.coveragerc`
- ADR-016, ADR-017, ADR-028
