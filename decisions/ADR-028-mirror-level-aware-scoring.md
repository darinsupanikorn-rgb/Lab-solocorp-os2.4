# ADR-028: Mirror Check Scoring ต้องแยกตามระดับ (L1/L2 = advisory)

**วันที่:** 2026-10-21
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — ตัดสินแล้วรายงาน Owner)
**ที่มา:** Deep system health check (21 ต.ค. 2569) · Owner อนุมัติเอง
**เกี่ยวกับ:** ADR-016 (behavior-centric routing) · ADR-027 (route_v2 signal gate)

---

## บริบท

`central_bus/mirror_check.py` ใช้เกณฑ์ผ่าน **60% เหมือนกันทุกระดับ (L1–L5)**

แต่ **คำถามของแต่ละระดับไม่ได้ถามสิ่งเดียวกัน**:

| ระดับ | คำถาม | ความหมายของคำตอบ NO |
|:--|:--|:--|
| **L1** (monitor) | "Decision นี้มี impact อะไรบ้าง?"<br>"Owner ควรรู้อะไรเกี่ยวกับ decision นี้?" | **"Owner ไม่ต้องรู้"** → ถูกต้องสำหรับงานระดับ L1 |
| **L2** (advisory) | "Dr.solodev จะเขียน code แบบนี้ไหม?" ฯลฯ | ข้อเสนอแนะ ไม่ใช่ gate |
| **L3+** | "Owner จะ approve ไหม?" / "สะท้อนตัวตนไหม?" | **"ไม่ผ่าน"** → ต้อง block + escalate |

→ การนับคำถาม L1 ที่ตอบ "Owner ไม่ต้องรู้" เป็น **fail** = **false negative**
→ งานที่ไม่มีปัญหาดูเหมือนถูก mirror จับ → เสียความหมายของทั้งระบบ

**หลักฐานจริง (รอบแรกหลังซ่อม mirror check, 21 ต.ค.):**
6 ข้อผ่าน 5 — ข้อเดียวที่ fail คืองานปรับ budget ของ perf test (ระดับ qa = L1)
→ LLM ตอบ "NO" ต่อคำถาม *"Owner ควรรู้อะไรเกี่ยวกับ decision นี้?"* → ซึ่งเป็นคำตอบที่**ถูก**
→ แต่ถูกนับเป็น fail (score 50% < 60%)

---

## ตัดสินใจ

**เกณฑ์ผ่านแยกตามระดับ:**

| ระดับ | พฤติกรรม | ผลกระทบ |
|:--|:--|:--|
| **L1, L2** | **advisory** — บันทึก score ไว้เสมอ แต่ `passed=True` → **ไม่ block** | 12/20 แผนก (L1: content_creator, psychology, qa, support, ui_designer · L2: design, engineering, legal, neteng, rd_lab, sales, web3) |
| **L3, L4, L5** | **gate** — `passed = score >= 60%` เหมือนเดิม **ไม่เปลี่ยน** | 8/20 แผนก (cfo, cmo, coo, cybersec, product, architect, orchestrator, ceo) |

**เพิ่มฟิลด์ `advisory` ใน `MirrorCheckResult`** → ผู้เรียกแยกได้ว่าเป็น advisory หรือ gate
- `to_dict()` ส่ง flag ออกไป
- audit log เพิ่ม `advisory` + `below_threshold` → **คะแนนต่ำยังถูกบันทึก** ไม่หาย
- `reason` ระบุชัดว่าเป็น advisory และเตือนเมื่อคะแนน < 60%

---

## เหตุผล

1. **Mirror คือเครื่องมือ "ช่วยคิด" ไม่ใช่ "ตัดสิน"** ที่ระดับ L1/L2 ความหมายคือบันทึกข้อมูลประกอบให้คนดู — การ block ที่นี่คือการบล็อกงานที่ไม่มีปัญหา
2. **ไม่ให้หลุด gate ที่จริงจัง** — L3+ ยัง block เหมือนเดิมทุกประการ (ไม่เปลี่ยนพฤติกรรมเดิมของระดับที่ตัดสินใจเงิน/สถาปัตยกรรม/วิสัยทัศน์)
3. **คะแนนไม่หาย** — advisory ≠ ไม่สนใจ → บันทึกคะแนน + `below_threshold` ไว้ใน audit ทุกครั้ง
4. **สอดคล้องกับ escalation filter** — L1–L2 คือ "agent_executes" ตาม `rules/01-receive.md` → ไม่ควรต้องผ่าน mirror gate

---

## ผลกระทบที่ต้องรู้

1. **12/20 แผนกไม่ block อีก** — ระดับ L1/L2 จะไม่หยุดงานแม้ mirror ไม่ผ่าน
   → การ escalate ยังทำได้ผ่าน `rules/01-receive.md` §Escalation Filter (L3+ → CEO/Owner) ซึ่งเป็นคนละชั้นกับ mirror check
2. **LLM ไม่ deterministic** — score ของคำถามเดิมเปลี่ยนระหว่างรอบ (ข้อ qa L1: 50% → 0%)
   → mirror check เป็น **สัญญาณประกอบ** ไม่ใช่ตัวตัดสิน — อย่าตัดสินใจจาก 1 รอบ
3. **`require_mirror_check(min_level=...)` ยังทำงานเหมือนเดิม** — ยัง 403 เมื่อระดับแผนกต่ำกว่า `min_level` ที่ skill กำหนด (เช่น skill L3 จะไม่รับแผนก L1/L2)

---

## ผลการทดสอบ

- `tests/test_mirror_level_scoring.py` — 6 เคส (L1/L2 advisory ไม่ block · score ยังบันทึก · L3+ ยัง block · L3+ ที่ผ่านยังผ่าน · flag ไปถึง `to_dict`)
- verify end-to-end: qa (L1) → score=0, advisory=True, **passed=True** · engineering (L2) → score=66, advisory=True, passed=True

---

## References
- `central_bus/mirror_check.py` — `MIRROR_QUESTIONS`, `run_mirror_check()`, `MirrorCheckResult`
- `rules/01-receive.md` §2 — Escalation Filter (L1–L5)
- `rules/02-work.md` §3 — Communication Pattern
- `profiles/CERTIFICATION-REGISTRY.md` — ผู้ตรวจ/ผู้อัปเดต
