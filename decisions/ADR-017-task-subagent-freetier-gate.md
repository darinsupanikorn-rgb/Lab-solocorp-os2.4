# ADR-017: Task Subagent Free-Tier Gate + นโยบาย Delegation ชั่วคราว

**วันที่:** 2026-10-14
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — ตัดสินแล้วรายงาน Owner)
**ที่มา:** Owner รายงานว่าเรียกแผนกอื่นใน OpenCode แล้วเจอ `OpenCode's free tier can only be used from within OpenCode`

---

## บริบท

ทุก custom subagent ใน `.opencode/agents/` (19 ไฟล์) ถูก pin โมเดล `opencode/muse-spark-1.3-contributor-free`
(commit `cc99156`) — จุดประสงค์เดิมคือรวมทุก agent ให้ใช้โมเดลฟรีตัวเดียว หนี model churn

เมื่อ delegate ผ่าน Task/`@mention` บน OpenCode Desktop v1.18.34 → child session ล้มด้วย free-tier error
ทั้งที่แชทหลักใช้โมเดลเดียวกันรอดปกติ

## การสืบสวน (หลักฐาน 2 สนามตรงกัน)

| เทสต์ | Desktop (Owner) | Harness (CEO) |
|:------|:----------------|:--------------|
| แชทหลัก ceo-hanuman + muse-spark | ✅ รอด | ✅ รอด |
| CLI `opencode run` + muse-spark | — | ✅ รอด (โมเดลไม่ตาย) |
| Task → `explore` (built-in, read-only) | ✅ รอด | ✅ รอด 2/2 |
| Task → `general` (built-in, full tools) | ❌ แถวแดง + fallback | ❌ ร่วง |
| Task → custom full-tools (changful ฯลฯ) | ❌ แถวแดง + fallback | ❌ ร่วง |
| Task → custom **read-only probe** (`scout-boundary-test`, deny edit/bash/task) | ❌ `Error: OpenCode's free tier can only be used from within OpenCode.` (Task ID `ses_ec9ef1…`) | — (probe อยู่แค่ Desktop) |

สอดคล้องกับ issue ต้นน้ำ: `#50806` (custom subagent spawn fail), `#53347`
(custom agent โดน deny บน Desktop v1.18.34 ทั้งที่ built-in ใช้โมเดลเดียวกันผ่าน),
`#49680` (ด่านเข้มตั้งแต่กลาง ก.ย. 2026)

## Root Cause

**ด่าน free-tier ของ provider `Console` ปฏิเสธ child session ที่ไม่ใช่ `explore`** —
ไม่เกี่ยวกับ `model:` pin (ถอด pin แล้วยังร่วงเหมือนเดิม, commit `d482f17` พิสูจน์แล้ว)
และไม่เกี่ยวกับ toolset (probe แบบ read-only ที่โคลน dept agent มาทุกอย่างยกเว้นสิทธิ์ ก็ยังโดน)
เป็นบั๊กฝั่ง OpenCode (child session ไม่พก entitlement flag "from within OpenCode" ติดไป)
แก้จาก repo เราไม่ได้ — ต้องรอ upstream patch

## ข้อตกลง (Decision)

1. **คง `d482f17` ไว้** (ถอด `model:` pin ออกจาก 19 subagents) — ไม่ใช่ยาแก้ แต่เป็นท่าที่ถูกต้อง
   ตาม docs (inherit parent session model) และไม่เป็นโทษ (effective model เท่าเดิม)
2. **`/workspace [แผนก] [งาน]` เป็นทางหลักชั่วคราว** สำหรับ delegate ข้ามแผนกบน Desktop
   (เปิดห้องแชทแยกพร้อม context bundle — ไม่ผ่านด่าน child-session เลย ไม่โดนบั๊กนี้)
3. **Task/`@mention` ใช้ได้เฉพาะ `@explore`** (งาน read-only: ค้นโค้ด, วิจัย) — นอกนั้นห้ามใช้จนกว่า
   upstream จะแก้ (ดูเงื่อนไขข้อ 4)
4. **เงื่อนไขคืนค่า:** เมื่อ OpenCode ออกเวอร์ชันที่แก้เรื่องนี้ → รันเมทริกซ์เทสต์เดิมซ้ำ
   (`@general` + custom ต้องรอด) → ถอดนโยบายข้อนี้ออก + บันทึกใน ADR ฉบับนี้

## ผลกระทบ

### Positive
- องค์กรไม่สะดุด — มีทางหลักที่รอดชัวร์ (`/workspace` สร้างไว้ตั้งแต่ `6327143`)
- ไม่เสียเวลาวนไล่ config ที่ไม่ใช่ต้นเหตุอีก

### Risks & Mitigation
| Risk | Impact | Mitigation |
|:-----|:-------|:-----------|
| `/workspace` หนักกว่า Task (เปิดแชทใหม่ทุกครั้ง) | Medium | ใช้เฉพาะงานข้ามแผนก, งานอ่านอย่างเดียวใช้ `@explore` |
| Upstream ไม่แก้ซักที | Low | สถาปัตยกรรมนี้ใช้งานได้ถาวรอยู่แล้ว |
| คนลืมแล้วกลับไปใช้ `@mention` | Medium | กฎใน `rules/01-receive.md` + CEO ทักเมื่อเห็นแถวแดง |

## หลักฐาน
- Screenshot Desktop 4 ชุด (eng-fail, general-fail, explore-pass, probe-fail + Task ID)
- Commit `d482f17` (19 ไฟล์, ถอด model pin) + เมทริกซ์เทสต์ใน session-log
- Probe file `scout-boundary-test.md` ถูกลบหลังจบการวินิจฉัย (ไม่เก็บของชั่วคราวใน roster)
