# ADR-027: route_v2 เชื่อ classifier เมื่อมี signal (>0)

**วันที่:** 2026-10-14 (ต้นฉบับ) · 2026-10-21 (Part 2 — ปรับให้ตรงกับ implementation จริง)
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — ตัดสินแล้วรายงาน Owner)
**ที่มา:** PR #19 (darinsupanikorn-rgb) — รีวิว + merge เฉพาะส่วนโค้ดกลาง
**Supersedes:** กฎ confidence ≥ 0.9 ใน ADR-016 §แนวคิด (เฉพาะ route_v2)
**หมายเหตุ:** เลข ADR-017 ถูกจองไปแล้วโดย `ADR-017-task-subagent-freetier-gate.md` → renumber เป็น ADR-027 ตอน merge

---

## บริบท

ADR-016 กำหนดว่า confidence ≥ 90% ถึง route อัตโนมัติ ต่ำกว่านั้นส่ง CEO review
`route_v2` / `route_v2_sync` จึงมี gate `confidence >= 0.9`

แต่ใน data regime ปัจจุบัน confidence สูงสุดที่ classifier ผลิตได้คือ ~0.3–0.45
(ML บนข้อมูลน้อย + keyword scoring แบบ normalized) — ไม่มี input ธรรมชาติอันไหน
ผ่าน 0.9 เลย ผลคือ **v2 routing ตายทั้งระบบ** ได้แต่ fallback ไป CEO

ในขณะเดียวกัน test contract (`test_behavior_classifier.py::TestBehaviorRouter`)
กำหนดว่า input ชัดเจนต้อง route ถูกแผนก: budget→cfo, bug→engineering,
security→cybersec — ซึ่ง gate 0.9 ทำให้ตกทั้งหมด

## ตัดสินใจ

`route_v2` (async) และ `route_v2_sync` เชื่อผล classifier **เมื่อ confidence > 0.0**
(zero-signal เท่านั้นที่ fallback: `owner_decision` map ไป `ceo` อยู่แล้ว
ผลลัพธ์จึงเท่ากับ fallback เดิมพอดี)

## เหตุผล

1. Tests คือ executable contract — 3 ข้อเรียกร้องพฤติกรรมนี้โดยตรง
2. Gate 0.9 ไม่เคยมี input ผ่านใน regime ปัจจุบัน (วัดจริงสูงสุด ~0.45)
3. No-signal ยัง fallback เหมือนเดิม — ไม่เสีย safety net

## ความเสี่ยง + ทบทวน

- ถ้าวันไหน training data เยอะจน ML มั่นใจกลางๆ บ่อยๆ แล้ว misroute เพิ่ม
  ให้กลับมาทบทวน gate ใหม่ (เช่น tiered: >0.5 auto-route, ต่ำกว่านั้น review)
- ติดตามผ่าน test suite: ห้ามมี test_route_v2 ตก

---

## Part 2 — routing 3 จุด (2026-10-21, แก้ให้ตรงกับ implementation จริง)

> ⚠️ **Part 2 รุ่นแรกของ PR #19 เขียนไว้ไม่ตรงกับโค้ดจริง** — แก้ใหม่ตอน merge เข้า upstream
> (สาเหตุ: เขียน ADR ก่อนลงมือแก้ แล้วเลือกวิธีอื่นในตอน implement)

1. **Tier 1 keyword matching: first-match → best-match** (นับจำนวน keyword ที่ match)
   — *ไม่ได้*แก้ที่ `routing_rules.json` (ไม่ต้องสับสนลำดับไฟล์) แต่แก้ที่ `central_bus/router.py`
   `rule` ที่เฉพาะเจาะจงต้องชนะ `rule` กว้าง:
   `deploy smart contract on solana` → web3 (smart contract + solana = 2) ไม่ใช่ engineering (deploy = 1)
   tie → คงลำดับไฟล์เดิม (พฤติกรรมเดิม)
2. **`priority_for()` ข้าม rule ที่ `mirror_check=true`** — แก้ leak จริง
   `r_mirror_ceo` (priority=critical) เคยรั่วมาเซ็ต priority ของ**ทุก**ข้อความที่ไป CEO
   ตอนนี้ `priority_for('ceo')` = normal · แผนกอื่นไม่เปลี่ยน (มี rule หลักมาก่อนแล้ว)
   → ตรงกับข้อ 3 ของ Part 2 รุ่นแรก ("ceo mirror rule critical → normal") แต่แก้ที่ต้นเหตุ
3. **Fallback = COO (L3 gatekeeper)** — *แก้กลับจากรุ่นแรก*
   รุ่นแรกเขียนว่า "fallback coo → ceo" แต่โค้ดจริง fallback เป็น COO
   ตาม hierarchy Owner → CEO → COO → แก้ test ให้ตรงกับโค้ด (`test_route_fallback`)
   เหตุผล: COO คือ L3 gatekeeper — fallback ไป CEO (L4) แทนที่จะแก้ที่ COO แปลว่าข้าม gate

### ผล

- 3 failed → 0 (เหลือ 3 ตัวที่ต้องมี Docker + Linux bash → CI skip อัตโนมัติ)
- **verified upstream (Linux, 2026-10-21): 738 passed · 0 failed · coverage 74%**
- regression เดิม 26 failed → 0 failed (รวม 28 จุดจาก `behavior_classifier.py` / `dashboard.py` / `handoff_confirm.py` / `api_cli.py`)
