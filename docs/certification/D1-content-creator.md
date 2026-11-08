# D1 — Agent Rationale: `content-creator-sek` (Content Creator · เสก)

> ตาม `sop/TEMPLATE-D1-agent-rationale.md` · `rules/06-certification.md` §2
> **ผู้ทำ (maker):** CEO หนุมาน — ผู้ dispatch งานให้แผนก (เขียนแทนแผนก ไม่ใช่แทนผู้ตรวจ)
> **วันที่:** 2026-10-21 (rev.3 — rev.2 + แก้เกณฑ์ความยาวเป็นตัวอักษร) · **งาน/CMD:** แผน B — เดินบันได certification ตัวแรกให้ครบวง
> **สถานะ:** ส่งตรวจ Owner (default = ยังไม่ผ่าน)

---

## 0. สถานะจริงของโค้ดวันนี้ (ต้องอ่านก่อน — กัน overclaim)

`workers/agents/content_agent.py` **วันนี้เรียกแค่ `self.think()`** (`:97`) — **ไม่ได้เรียกเครื่องมือใดเลย**
`read_file`/`write_file`/`list_dir`/`run_command` มีอยู่ใน `base_agent.py` แต่ `ContentAgent.execute()` ไม่เคยใช้

→ เอกสารนี้จึงเป็น **แผน (rationale)** ไม่ใช่หลักฐานว่า implement แล้ว
→ **การทำให้เรียกเครื่องมือจริง + บันทึก tool-call log + ใส่ guard = งานของ D2**

**Re-scope:** D2 ของ `content-creator-sek` **ไม่ใช้** `scripts/content_render.py` อีก (199 บรรทัด) — ตอนนี้ **Concat รองรับ Linux ครบครัน** (.deb, .rpm, .AppImage, Flatpak, Arch) → สามารถรันบน Linux ได้จริง เฉพาะวิธีติดตั้งให้ถูกต้อง (ดู FAMILY.md:16, CERTIFICATION-REGISTRY.md:10)
→ D2 ใช้ `content_agent.py` (112 บรรทัด, รันได้ทุก OS) เป็นฐาน

---

## 1. งานคืออะไร

รับ **content brief** แล้วผลิต **draft โพสต์ LinkedIn** ออกมาเป็นไฟล์ `.md` ที่ตรวจสอบได้ — ไม่ใช่ตอบเป็นข้อความในแชท

**ขอบเขตงานรอบนี้ = 1 ประเภทเท่านั้น: LinkedIn social post** (blog/video/newsletter/caption = ขยายภายหลังพร้อมเกณฑ์ของตัวเอง)

**ผลลัพธ์ที่วัดได้:** brief 1 ไฟล์ → draft 1 ไฟล์ที่มี 4 องค์ประกอบ + ความยาวในช่วงที่กำหนด (ตัวอักษร) + tool-call log ที่ตรวจย้อนได้

---

## 2. ทำไมต้องใช้ agent

| เหตุผล | เงื่อนไขที่มนุษย์/script ทำแทนไม่ได้ |
|:--|:--|
| **อ่านหลายแหล่งต่อ 1 งาน** | ต้องอ่าน `profiles/03-cmo/SOUL.md` (marketing direction) + `profiles/01-ceo/SOUL.md` (brand voice) + `docs/brand/BRAND-GUIDELINES-v1.md` + brief — script ไม่รู้ว่าจะหยิบอะไร |
| **ตัดสินใจระหว่างทาง** | brief บอก "LinkedIn" แต่เนื้อหาเป็น technical → ต้องเลือก hook/tone/CTA ให้เหมาะ ไม่ใช่ template ตายตัว |
| **brief เปลี่ยนทุกครั้ง** | input เป็นภาษาธรรมชาติ (ไทย/อังกฤษ) — regex จะพังทันทีที่ถ้อยคำเปลี่ยน |
| **ต้อง "ลงมือ" ไม่ใช่ "ตอบ"** | ต้องเขียนไฟล์จริง ตรวจไฟล์จริง แล้วรายงานจากของจริง |

**script ทดแทนไม่ได้เพราะ:** `scripts/content_render.py` เป็น *renderer* (spec JSON → ประกอบไฟล์วิดีโอ) ตามที่มันเขียนเองว่า *"ไม่คิดเนื้อหาเอง"* (`:5-6`) — ไม่ใช่ *writer*

---

## 3. agent ตัวไหน + เครื่องมือที่ต้องใช้

**ตัวแทน:** `content-creator-sek` (`workers/agents/content_agent.py`, subclass ของ `BaseAgent`)

| เครื่องมือ | ใช้ทำอะไร | มีจริงไหม |
|:--|:--|:--|
| `read_file` | อ่าน SOUL ×2 + brand guidelines + brief | ✅ `base_agent.py:113` (ยังไม่ถูกเรียก — งาน D2) |
| `list_dir` | หา brief ในโฟลเดอร์ที่รับ | ✅ `:127` (ยังไม่ถูกเรียก) |
| `write_file` | เขียน draft ลง `bus/creative/drafts/` | ✅ `:120` (ยังไม่ถูกเรียก) |
| `run_command` | นับขนาด/ตรวจไฟล์ (`wc -m`, `test -f`) | ⚠️ `:138` — **วันนี้ไม่คืน exit code** (ต้องแก้ใน D2) |
| `think` | สร้างเนื้อหา (LLM) | ✅ `:62` (ตัวเดียวที่ใช้อยู่) |

**ไม่ใช้:** `web_read`/`web_search` (ต้องอนุมัติแยก) · `report_to_ceo` (ใช้เฉพาะเมื่อจบงานจริง)

---

## 4. ขอบเขตสิทธิ/เครื่องมือ

**ได้ทำ:** อ่าน `profiles/**`, `docs/brand/**`, `bus/creative/**` · เขียนไฟล์ **เฉพาะใต้ `bus/creative/drafts/`** · รันคำสั่งอ่านอย่างเดียว (`wc`, `test`, `ls`, `head`)

**ห้ามทำ (hard stop):**
- ⛔ ห้ามแก้ `profiles/**`, `rules/**`, `sop/**`, `decisions/**` — ground truth ขององค์กร
- ⛔ ห้ามเขียนนอก `bus/creative/drafts/`
- ⛔ ห้าม **โพสต์ออก platform จริง** (X/LinkedIn) — งานนี้คือ **draft only**
- ⛔ ห้ามรันคำสั่งลบ/ติดตั้ง/เครือข่าย (`rm`, `pip install`, `curl`)
- ⛔ ห้าม commit/push · ห้ามแตะ `.env`, คีย์, logic เงิน
- ⛔ **Visual assets = out of scope** รอบนี้ (SOUL §"Visual = non-negotiable" จะถูกครอบด้วยงานแยกในอนาคต — D1 นี้รับเฉพาะ text draft)

> ⚠️ **ความจริงที่ต้องยอมรับ: ข้อห้ามข้างบนยัง "ไม่ถูกบังคับ" ในโค้ดวันนี้**
> - `write_file` (`base_agent.py:120-125`) ทำ `mkdir(parents=True)` แล้วเขียน path ใดก็ได้ — **ไม่มี normalize/prefix check**
> - `run_command` (`:138-152`) ใช้ `shell=True` — **ไม่มี allowlist ใน repo**
>
> → **การใส่ guard ทั้งสอง = งาน D2 ที่ต้องมีหลักฐาน** (ไม่ใช่ของที่มีอยู่แล้ว)
> → จนกว่าจะมี guard: `ContentAgent` ถือว่า **ยังไม่ได้รับสิทธิ์เขียนไฟล์จริง** (D0 → ร่างได้เท่านั้น)

---

## 5. เส้นชัยของงานนี้

ผ่านเมื่อ **ครบทั้ง 6 ข้อ** — วัดด้วย script `scripts/verify_d2_content_agent.py` (ผู้ตรวจรัน ไม่ใช่ agent รันเอง)

| # | เกณฑ์ | วัดด้วย |
|:-:|:--|:--|
| 1 | อ่าน SOUL ครบ 2 ไฟล์ + brand guidelines | log มี `read_file` → `profiles/01-ceo/SOUL.md`, `profiles/03-cmo/SOUL.md`, `docs/brand/BRAND-GUIDELINES-v1.md` |
| 2 | อ่าน brief จริง | log มี `read_file`/`list_dir` → ไฟล์ brief ที่รับมา |
| 3 | เขียน draft จริง | ไฟล์ `.md` เกิดขึ้นใต้ `bus/creative/drafts/` |
| 4 | ครบ 4 องค์ประกอบ | ไฟล์มีหัวข้อ `## Hook`, `## Body`, `## CTA`, `## Hashtags` |
| 5 | ขนาดเหมาะสม (LinkedIn post) | `wc -m` → **600 ≤ จำนวนตัวอักษร ≤ 2500** (ไทยไม่มีช่องว่างระหว่างคำ → `wc -w` ใช้ไม่ได้ ให้รายงานเป็นข้อมูลประกอบเท่านั้น) |
| 6 | ไม่เขียนนอกขอบเขต | snapshot ไฟล์ก่อน/หลัง (find) — ไม่มีไฟล์ใหม่นอก `bus/creative/drafts/` (ไม่ใช้ `git status` เพราะ ignore ปิดบัง) |

**Log artifact:** `bus/evidence/2026-10-23/d2-content-creator/tool-calls.jsonl` — 1 บรรทัด/1 tool call `{"ts","tool","args","ok"}`
**คำสั่งที่กำหนด exit code:** `python scripts/verify_d2_content_agent.py --brief <path> --out <path>` → ต้องได้ **exit 0** (script ต้องอ่าน `returncode` เองได้ — แก้ใน D2)

**ไม่ผ่านถ้า:** ตอบข้อความเฉย ๆ โดยไม่เขียนไฟล์ · เขียนนอกขอบเขต · ใช้ tool นอก allowlist · ความยาวนอกช่วง · ไม่มี tool-call log

---

**ผู้ตรวจ (≠ ผู้ทำ):** **Owner (Dr.solodev)** — ตาม `rules/06-certification.md:16` + `SOP-06:22` (maker = CEO → checker ต้องเป็น Owner)
**ความเห็นผู้ตรวจอิสระ (advisory, ไม่ใช่การอนุมัติ):** pipeline-auditor — RETURNED rev.1, 4 blocking issues, ทั้งหมดถูกแก้ใน rev.2 นี้
**สถานะ:** ☑ **ผ่าน** (D1) · ☐ ส่งคืน
**อนุมัติโดย:** Owner (Dr.solodev) · **วันที่:** 2026-10-25 · rev.3 ไม่มีการแก้ไขเงื่อนไข
**เหตุผล/ข้อแก้:** Owner อนุมัติตามที่ส่ง — ขอบเขต "LinkedIn draft เท่านั้น" + ข้อห้ามที่ยังไม่ถูกบังคับในโค้ด (ข้อ 4) ถูกยกระดับเป็นงาน D2 ครบแล้ว (path guard ใน `_write`, allowlist คำสั่งใน `_verify`, tool-call log) → ดูหลักฐาน D2 ที่ `bus/evidence/2026-10-25/d2-content-creator/`

> **หมายเหตุหลังอนุมัติ (ไม่เปลี่ยนเงื่อนไข):** ตัวเลขในเอกสารอ้าง 841 tests / 20 แผนก ณ 21 ต.ค. — วันนี้ 868 tests (เพิ่มเทสต์ ไม่ได้ลดเกณฑ์ใด) · D2 รันซ้ำกับโค้ดวันนี้ได้ 6/6 ✅ exit 0
