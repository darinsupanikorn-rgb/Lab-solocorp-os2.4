# SOP-02: Escalation — L1-L5 Decision Filter

**Owner:** CEO หนุมาน (L1-L4), Owner (L5)  
**Version:** v1.0  
**Applies to:** All Department Heads → CEO → Owner

## Core Principle

> Owner ต้องตัดสินใจแค่ 20-30% — ทีม operate 70-80%

## L1-L5 Framework

```
L1: Auto (Loop Runner / Scripts / Cron)
  → ไม่ต้องถามใคร, ทำเลย
  → Example: brain_auto_commit, daily_brief

L2: Specialist Agent
  → Agent ตัดสินใจเอง
  → Example: deploy, fix bug, routine task
  → Record ใน evidence เท่านั้น

L3: Department Head
  → หัวหน้าตัดสินใจ
  → ถ้า < 3 departments → Head-to-Head โดยตรง
  → Report กลับ CEO: "ทำแล้ว" / "มี issue"

L4: CEO (หนุมาน)
  → Decision ที่ impact 3+ departments
  → Budget/Strategy/Forecast
  → CEO ตัดสินใจ → รายงาน Owner ตอนจบ (3-line)

L5: Owner (Dr.solodev)
  → Vision Change
  → Organization Restructure
  → Core Product Pivot
  → เปลี่ยน Mission Statement
```

## Escalation Flow

```
Request → Level Classification
  ├── L1 → Auto-execute → Done
  ├── L2 → Agent execute → Record evidence
  ├── L3 → Head decide → Report to CEO
  ├── L4 → CEO decide → Report to Owner (end)
  └── L5 → CEO brief → Owner decide → Execute
```

## เมื่อ Head ไม่แน่ใจ

- Consult CEO หนุมาน ก่อน escalate ไป Owner
- CEO = gatekeeper L5 — Owner ต้องไม่โดน L1-L4 รบกวน

## Violation

- L1-L4 ที่ส่งถึง Owner โดยไม่จำเป็น = **system failure** — ต้อง root cause analysis
