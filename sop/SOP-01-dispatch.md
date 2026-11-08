# SOP-01: CEO Dispatch — ส่งงานไป Department

**Owner:** CEO หนุมาน  
**Version:** v1.0  
**Applies to:** CEO → Department Heads

## Step-by-Step

### 1. Input
- รับ request/vision/task จาก Owner หรือ detect เอง
- ต้องผ่าน **Mirror Check** ก่อน (L3+: 3 คำถาม)

### 2. Classify Level
| Level | Criteria | Action |
|:-----:|:---------|:-------|
| L5 | Vision change, org restructure, core product | สรุป brief → ถึง Owner |
| L4 | Cross-dept strategy, big budget, roadmap shift | CEO ตัดสินใจ → dispatch → รายงาน |
| L3 | Feature decision, cross-dept handoff | Dispatch by CEO → Heads ตัดสินใจ |
| L2 | Bug fix, deploy, daily ops | Dispatch → Agent ทำเลย |
| L1 | Routine, auto | Loop Runner |

### 3. Dispatch
- สร้าง structured command: `bus/dispatch/YYYY-MM-DD/CMD-NNN-name.json`
- ระบุ: tasks, priority, deadline, acceptance criteria, artifacts
- บันทึกใน `bus/queue/high.jsonl` หรือ `normal.jsonl`

### 4. Follow-up
- L1-L3: ไม่ต้องรายงาน Owner — แค่ record
- L4: สรุปสั้นเมื่อเสร็จ
- L5: Owner ได้เห็นก่อน action

### 5. Completion
- Department Head report กลับเมื่อเสร็จ
- Evidence ถูกบันทึกใน `bus/evidence/`
- ถ้าเกิน deadline โดยไม่ report → Auto-escalate

## Checklist
- [ ] Mirror Check ผ่าน?
- [ ] Level ถูกต้อง?
- [ ] Tasks ชัดเจน มี acceptance criteria?
- [ ] Deadline realistic?
- [ ] Record ใน queue?
