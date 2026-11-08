# SOP-05: Incident — ระบบมีปัญหา

**Owner:** CEO หนุมาน (escalate ตามระดับ)  
**Version:** v1.0  
**Applies to:** All Department Heads → CEO

## Severity Levels

| Level | อะไร | Response | ถึง Owner? |
|:-----:|:-----|:---------|:----------:|
| 🔴 **CRIT** | System down, data loss, security breach | ตอบสนอง 5 นาที | ✅ แจ้ง Owner ทันที |
| 🟡 **HIGH** | Major feature down, pipeline blocked | ตอบสนอง 30 นาที | รายงานหลังแก้ |
| 🟠 **MED** | Non-critical bug, partial failure | ตอบสนอง 2 ชม. | ไม่ต้อง |
| 🟢 **LOW** | Minor issue, cosmetic | ตอบสนอง 24 ชม. | ไม่ต้อง |

## Flow

### 1. Detect
- Monitor Watchdog / Exception Triage / Agent / User report

### 2. Classify
- ระดับ? (CRIT/HIGH/MED/LOW)
- Department ที่เกี่ยวข้อง?

### 3. Triage (Exception Triage Agent)
- Root cause analysis ภายใน 5-30 นาที
- Auto-resolve (ถ้าเป็น pattern ซ้ำ)

### 4. Resolve
- Fix → QA verification → Deploy
- บันทึก evidence

### 5. CRIT only: Post-mortem
- เขียน `incident-postmortem` skill
- สรุป: timeline + root cause + fix + lesson learned
- Owner รับทราบ (L5)

## Auto-Response

| Pattern | Auto-Response |
|:--------|:--------------|
| Service down | Auto-restart |
| Queue backlog | Scale up poll rate |
| Known error pattern | Apply known fix |
| New error | Log → triage → create ticket |
