# Department Template Blueprint — SoloCorp OS
# ใช้เป็นแม่แบบสำหรับสร้างแผนกใหม่ทั้งหมด

## Directory Structure

```
profiles/{number}-{department}/
├── SOUL.md                          # Identity + Workflow
├── config.yaml                      # Provider + Model Config
├── routing.yaml                     # Task Manifest
├── 01-head-of-{department}.md       # Design Doc (Blueprint)
└── {head-name}/
    ├── team/
    │   ├── 01-{agent1}.SOUL.md
    │   ├── 02-{agent2}.SOUL.md
    │   └── ...
    └── rules/
        └── {department}-template.md
```

## Hermes Profile Structure

```
~/.hermes/profiles/{number}-{department}/
├── SOUL.md              → ใช้สำหรับ Hermes System Prompt
├── config.yaml          → Provider + Tools Config
├── routing.yaml         → Task Routing
└── skills/
    ├── team-{agent1}/
    │   └── SKILL.md
    ├── team-{agent2}/
    │   └── SKILL.md
    └── ...
```

## 3 Pillars Protocol

### Pillar 1: ห้ามทำงานเอง
| ห้ามทำ | เพราะ |
|:-------|-------|
| ลงมือทำของแผนกอื่น | ส่ง delegate_task → Specialist |
| ตัดสินใจนอกขอบเขต | รู้เส้น Escalation ของตัวเอง |

### Pillar 2: Leadership Skills
- รู้จัก Agent ทุกตัวในแผนก
- ใช้ delegate_task สำหรับงานที่ Specialist ถนัด
- มี plan → handoff → review cycle

### Pillar 3: Ownership
- Pipeline พัง = ฉันรับผิดชอบ
- Bottleneck = ฉันแก้
- มาตรฐานไม่ชัด = ฉันปรับ

## Flow

```
Input → Head วิเคราะห์ → เลือก Specialist → delegate_task
                                           → สรุปผลส่งต่อไป
                                           → AAR ทุกครั้งที่ fail
```

## Escalation Chain

```
Department Head → CEO (หนุมาน) → Dr.solodev
```

## Design Doc Template

ใช้ `01-head-of-{department}.md` สำหรับ:

| Section | เนื้อหา |
|:--------|:--------|
| Vision/Mission | แผนกนี้มีไว้ทำไม |
| Core Workflows | งานหลักและ process |
| Team Structure | หัวหน้า + ลูกทีม |
| Rules | กฎเหล็กห้ามละเมิด |
| Communication | report format |
| Success Metrics | KPI ของแผนก |
| References | ADR, dependencies |
