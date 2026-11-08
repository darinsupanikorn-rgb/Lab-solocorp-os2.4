# ADR-003: Central Bus Schema + Protocol

**วันที่:** 2026-06-26
**สถานะ:** Accepted ✅
**Version:** v0.2.0

---

## สารบัญ

1. [บริบท](#1-บริบท)
2. [ปัญหา](#2-ปัญหา)
3. [ข้อตกลง (Decision)](#3-ข้อตกลง-decision)
4. [Central Bus JSON Schema](#4-central-bus-json-schema)
5. [Central Bus Protocol](#5-central-bus-protocol)
6. [Workflow Routing Rules](#6-workflow-routing-rules)
7. [Outbound Notification Template](#7-outbound-notification-template)
8. [Handoff Protocol Template สำหรับ Department Heads](#8-handoff-protocol-template-สำหรับ-department-heads)
9. [Pipeline Design Rules](#9-pipeline-design-rules)
10. [ผลกระทบ](#10-ผลกระทบ)
11. [แนวทางการ Implement](#11-แนวทางการ-implement)
12. [อ้างอิง](#12-อ้างอิง)

---

## 1. บริบท

จากการออกแบบ Department Architecture ใน Lab-solocorp-os2.4 เราต้องการระบบกลางสำหรับ **Data Layer** ที่ Agent ทุกตัวสามารถเขียน/อ่านข้อมูลได้โดยไม่ต้องผ่าน Department Head (ตาม ADR-002 Two-Tier Architecture)

Google AI Insights เสนอแนวคิด **Central Bus Agent** หรือ **Environment State Agent** — ตัวเดียว — ที่ทำหน้าที่เหมือนระบบ ERP/Jira ส่วนกลาง

## 2. ปัญหา

- **ไม่มีระบบกลาง:** Agent ต้องส่งงานถึงกันโดยตรง → Mesh Communication → ระบบพัง (n(n-1)/2 channels)
- **หัวหน้างานล้น:** ถ้าข้อมูลทุกชิ้นต้องผ่าน Department Head → Context Window ล้น
- **Pipeline ไม่มีมาตรฐาน:** Routing ระหว่างแผนกไม่มีระบบ, แต่ละแผนกทำตามใจ
- **ยากในการติดตาม:** เมื่อ Pipeline มี 10+ ขั้นตอน ไม่มีใครรู้ว่างานตอนนี้อยู่ที่ Stage ไหน

## 3. ข้อตกลง (Decision)

ประกาศ **Central Bus Architecture** เป็นระบบกลางของ Data Layer ใน Lab-solocorp-os2.4:

1. ทุก Agent ในระบบอ่าน/เขียนข้อมูลที่ Central Bus เท่านั้น
2. **ไม่มี Agent คุยข้ามสายโดยตรง** — ต้องผ่าน Central Bus หรือ Pipeline Route เสมอ
3. Central Bus ใช้ **JSON Schema** ตามที่ Google AI กำหนด
4. Central Bus Protocol ใช้ **Input → Process → Output** pattern
5. Workflow Routing Rules ถูกตั้งค่าโดย **Head of Orchestration**
6. Department Heads เห็นแค่ **Notification + Summary** จาก Bus
7. Agent รู้แค่ **2 สิ่ง** (รับจากใคร → ส่งให้ใคร)

---

## 4. Central Bus JSON Schema

### โครงสร้างหลัก (Root)

```json
{
  "project_id": "PRJ-2026-XXX",
  "global_status": "PENDING | IN_PROGRESS | COMPLETED | BLOCKED | CANCELLED",
  "current_phase": "PHASE_NAME",
  "phase_sequence": [
    "marketing_planning",
    "engineering_development",
    "qa_testing",
    "design_review",
    "marketing_launch"
  ],
  "departments_state": {},
  "workflow_routing_rules": {},
  "metadata": {
    "created_at": "2026-06-26T12:00:00Z",
    "updated_at": "2026-06-26T12:00:00Z",
    "version": "1.0.0",
    "owned_by": "Head of Orchestration"
  }
}
```

### departments_state — แต่ละ Department

```json
{
  "departments_state": {
    "orchestration": {
      "status": "COMPLETED",
      "artifacts_summary": "Pipeline defined, routing rules set",
      "raw_data_pointer": "bus://PRJ-2026-XXX/orchestration/",
      "handoff_history": [
        {
          "from": "CEO",
          "to": "Orchestration",
          "timestamp": "2026-06-26T08:00:00Z",
          "action": "GOAL_SET"
        }
      ],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "marketing": {
      "status": "IN_PROGRESS | COMPLETED | BLOCKED | PENDING",
      "artifacts_summary": "...",
      "raw_data_pointer": "bus://PRJ-2026-XXX/marketing/",
      "handoff_history": [],
      "current_task_id": "TASK-MKT-001",
      "completed_tasks": ["TASK-MKT-000"],
      "blockers": []
    },
    "engineering": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/engineering/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "design": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/design/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "qa": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/qa/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "finance": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/finance/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "sales": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/sales/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "product": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/product/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    },
    "legal": {
      "status": "PENDING",
      "artifacts_summary": null,
      "raw_data_pointer": "bus://PRJ-2026-XXX/legal/",
      "handoff_history": [],
      "current_task_id": null,
      "completed_tasks": [],
      "blockers": []
    }
  }
}
```

### workflow_routing_rules — กฎการส่งต่องาน

```json
{
  "workflow_routing_rules": {
    "on_marketing_planning_completed": {
      "trigger": "engineering_development",
      "notify": ["Head of Engineering", "Head of Orchestration"],
      "condition": null,
      "auto_route": true
    },
    "on_engineering_development_completed": {
      "trigger": "qa_testing",
      "notify": ["Head of QA", "Head of Orchestration"],
      "condition": "marketing_planning.artifacts_summary != null",
      "auto_route": true
    },
    "on_qa_testing_completed": {
      "trigger": "design_review",
      "notify": ["Head of Design", "Head of Orchestration"],
      "condition": "qa_testing.status == 'COMPLETED'",
      "auto_route": true
    },
    "on_design_review_completed": {
      "trigger": "marketing_launch",
      "notify": ["Head of Marketing", "Head of Orchestration"],
      "condition": null,
      "auto_route": true
    },
    "on_marketing_launch_completed": {
      "trigger": "project_completion",
      "notify": ["CEO", "Head of Orchestration"],
      "condition": null,
      "auto_route": false
    },
    "on_any_blocker": {
      "trigger": "exception_handler",
      "notify": ["Head of Orchestration"],
      "escalate_after_minutes": 120,
      "escalate_to": ["CEO"]
    }
  }
}
```

### Error/Exception Schema

```json
{
  "exception": {
    "project_id": "PRJ-2026-XXX",
    "type": "BLOCKER | TIMEOUT | DATA_CONFLICT | ROUTE_FAILURE",
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "source_department": "engineering",
    "message": "Engineering development exceeding deadline by 2 days",
    "details": {},
    "reported_by": "Head of Engineering",
    "reported_at": "2026-06-26T14:00:00Z",
    "assigned_to": "Head of Orchestration",
    "status": "OPEN | IN_PROGRESS | RESOLVED | ESCALATED"
  }
}
```

---

## 5. Central Bus Protocol

Protocol ใช้ **Input → Process → Output** Pattern ตามที่ Google AI ให้ไว้

### 5.1 Input — การอัปเดตจาก Agent ทุกตัว

**กฎ:**
- ห้าม Agent ข้ามแผนกคุยกันเองโดยไม่ผ่าน Bus
- Agent อัปเดตเฉพาะ `departments_state.<department_name>` ของตัวเองเท่านั้น
- Agent ไม่สามารถแก้ไข `workflow_routing_rules` ได้ (มีแค่ Head of Orchestration)

**Input Format:**

```json
{
  "action": "UPDATE_STATE | REPORT_COMPLETION | REPORT_BLOCKER | REQUEST_HANDOFF",
  "sender": {
    "agent_id": "engineering-agent-v1",
    "department": "engineering",
    "department_head": "Head of Engineering"
  },
  "project_id": "PRJ-2026-XXX",
  "payload": {
    "status": "COMPLETED",
    "artifacts_summary": "พัฒนา Landing Page เสร็จ — responsive + SEO",
    "raw_data_pointer": "db://engineering/repo_PRJ-001_landing",
    "completed_tasks": ["TASK-ENG-001", "TASK-ENG-002"],
    "blockers": []
  },
  "timestamp": "2026-06-26T12:00:00Z"
}
```

### 5.2 Processing — การประมวลผลโดย Central Bus

Central Bus ดำเนินการตามลำดับ:

```
Step 1: Parse Sender
  → ตรวจสอบ sender.department + sender.agent_id
  → ตรวจสอบว่า Agent มีสิทธิ์อัปเดต department นั้นหรือไม่

Step 2: Validate Payload
  → ตรวจสอบ JSON Schema compliance
  → ตรวจสอบ required fields (status, artifacts_summary)
  → ถ้า invalid → ส่ง error กลับ + log

Step 3: Update departments_state
  → เขียนข้อมูลลง departments_state.<sender.department>
  → อัปเดต metadata.updated_at
  → ตรวจสอบสถานะใหม่

Step 4: Check Workflow Routing Rules
  → ถ้า status == 'COMPLETED' → ดู workflow_routing_rules
  → ค้นหา trigger ที่ตรงกับ `<department>_completed`
  → ถ้า condition == null หรือ condition pass → ดำเนินการ Step 5
  → ถ้า condition fail → รอ (pending)

Step 5: Execute Routing
  → อัปเดต current_phase = target phase
  → สร้าง Notification (ตาม Outbound Template)
  → ส่ง Notification ไป Department Head ปลายทาง
  → ถ้า auto_route == true → trigger Agent ปลายทางอัตโนมัติ
```

### 5.3 Output — Notification ถึง Department Head

**รูปแบบ Notification (ตาม Google AI):**

```json
{
  "notification": {
    "to": "Head of [Department]",
    "type": "WORK_HANDOFF | STATUS_UPDATE | EXCEPTION_ALERT",
    "project_context": "1-sentence summary ของโปรเจกต์",
    "current_trigger": "ทำไมถึงถูกแจ้งเตือน?",
    "high_level_summary": [
      "สรุปสั้น bullet point 1",
      "สรุปสั้น bullet point 2",
      "สรุปสั้น bullet point 3"
    ],
    "data_access_link": "bus://PRJ-2026-XXX/<department>/",
    "expected_action": "สิ่งที่ Department Head ต้องทำต่อไป",
    "timestamp": "2026-06-26T12:00:00Z"
  }
}
```

**Example Notification:**

```json
{
  "notification": {
    "to": "Head of Engineering",
    "type": "WORK_HANDOFF",
    "project_context": "Project PRJ-2026-001: สร้าง Campaign สินค้าใหม่",
    "current_trigger": "Marketing วางแผนเสร็จ → ส่งต่องานพัฒนา Landing Page",
    "high_level_summary": [
      "Marketing PRD เสร็จ ✓",
      "Target: กลุ่มลูกค้าวัย 25-35",
      "ต้องการ Landing Page + ระบบสมัครสมาชิก"
    ],
    "data_access_link": "bus://PRJ-2026-001/marketing/",
    "expected_action": "เริ่มพัฒนา Landing Page — ดูรายละเอียดใน Central Bus",
    "timestamp": "2026-06-26T12:00:00Z"
  }
}
```

---

## 6. Workflow Routing Rules

### Dependency Chain — ลำดับ Pipeline พื้นฐาน

```
CEO → Orchestration → Marketing → Engineering → QA → Design → Marketing(Launch) → CEO
```

### Rule Types

| Rule Type | คำอธิบาย | Example |
|:----------|:---------|:--------|
| `on_<dept>_completed` | เมื่อแผนกนี้ทำงานเสร็จ | `on_marketing_completed` |
| `on_<dept>_blocked` | เมื่อแผนกนี้มีปัญหา | `on_engineering_blocked` |
| `on_any_blocker` | เมื่อมี blocker ที่ไหนก็ตาม | ใช้ escalate |
| `on_phase_timeout` | เมื่อ Phase นี้ใช้เวลาเกินกำหนด | `on_engineering_timeout` |

### Condition Syntax

| Operator | ความหมาย | Example |
|:---------|:---------|:--------|
| `==` | เท่ากับ | `"qa.status == 'COMPLETED'"` |
| `!=` | ไม่เท่ากับ | `"marketing.artifacts_summary != null"` |
| `in` | อยู่ในเซต | `"status in ['COMPLETED', 'REVIEWED']"` |
| `and` | และ | `"eng.status == 'COMPLETED' and qa.status == 'COMPLETED'"` |
| `or` | หรือ | `"design.status == 'COMPLETED' or marketing.status == 'COMPLETED'"` |

### Auto-Route Flag

| `auto_route` | ความหมาย |
|:------------:|:---------|
| `true` | เมื่อ Trigger → Central Bus ส่ง Notification ไป Department Head อัตโนมัติ + แจ้ง Agent ปลายทาง |
| `false` | เมื่อ Trigger → ส่งแค่ Notification, รอ Department Head ตัดสินใจ |

---

## 7. Outbound Notification Template

### Notification Template สำหรับทุก Department Head

**หัวข้อ:** `[PROJECT] — [ACTION] → [DEPARTMENT]`

```text
---
เรื่อง: งานใหม่จาก {sender_department} → {target_department}
โปรเจกต์: {project_name}
สถานะ: {current_phase} → {next_phase}
---

{sender_department} {action} เสร็จเรียบร้อย ✓

สิ่งที่ {target_department} ต้องทำ:
{expected_action_1}
{expected_action_2}
{expected_action_3}

รายละเอียดเพิ่มเติม: {data_access_link}
---

แจ้งเตือนโดย: SoloCorp OS Central Bus
Timestamp: {timestamp}
```

### Notification สำหรับException

```text
---
เรื่อง: ⚠️ Pipeline Alert — {project_id}
ประเภท: {exception_type}
ระดับ: {severity}
---

{error_message}

แผนกที่เกี่ยวข้อง: {source_department}
เวลาที่เกิด: {timestamp}

สิ่งที่ต้องทำ: {expected_action}
---
```

---

## 8. Handoff Protocol Template สำหรับ Department Heads

ตามข้อกำหนดจาก CEO — ทุก Department Head ต้องมี Handoff Protocol ใน SOUL.md โดยใช้ Template นี้:

### 8.1 Handoff Template

```json
{
  "handoff": {
    "from": "[Department Head Name]",
    "to": "[Target Department Head Name]",
    "project_id": "PRJ-2026-XXX",
    "phase": "[CURRENT_PHASE]",
    "status": "HANDOFF",
    "goal": "เป้าหมายสั้น 1 ประโยค",
    "deliverable": "สิ่งที่ต้องการจาก Department Head ปลายทาง",
    "deadline": "YYYY-MM-DD",
    "depends_on": ["department_A", "department_B"],
    "central_bus_ref": "bus://PRJ-2026-XXX/state",
    "timestamp": "2026-06-26T12:00:00Z"
  }
}
```

### 8.2 กฎ Handoff Protocol

1. **ทุก Handoff ต้องมี `central_bus_ref`** — ชี้ไปที่ state ใน Central Bus
2. **ทุก Handoff ต้องมี `goal`** — สั้น 1 ประโยค บอกว่าต้องการอะไร
3. **ทุก Handoff ต้องมี `deliverable`** — สิ่งที่ Department Head ปลายทางต้องส่งมอบ
4. **ทุก Handoff ต้องมี `timestamp`** — เพื่อ Audit Trail
5. **ถ้าเป็น Handoff ข้ามสายงาน** — ต้องมี `depends_on` บอกว่าแผนกไหนต้องเสร็จก่อน

### 8.3 การเขียน Handoff Protocol ใน SOUL.md

ทุก Department Head ต้องมีหัวข้อ `## Handoff Protocol` ใน SOUL.md ของตัวเอง
โดยระบุ:

- **เมื่อรับงาน:** Input → Process → Output
- **เมื่อส่งต่องาน:** ไปใคร พร้อม Payload อะไร
- **เมื่อรับ Exception:** ใครเป็นคน escalate, ขั้นตอนอะไร

---

## 9. Pipeline Design Rules

สืบทอดจาก CEO Turbo — กฎที่ละเมิดไม่ได้สำหรับทุก Pipeline:

### Rule 1: Agent รู้แค่ 2 ทิศทาง

```
Agent A รู้แค่: รับจากใคร → ส่งให้ใคร
Agent A ไม่รู้: ว่า Agent B ส่งต่อให้ใคร
Agent A ไม่สน: ว่า Pipeline มีกี่ขั้นตอน
```

### Rule 2: ห้าม Agent คุยข้ามสาย

```
❌ Marketing Agent → Engineering Agent (โดยตรง)
✅ Marketing Agent → 📦 Central Bus → Engineering Agent
```

### Rule 3: Pipeline = Sequential, Not Mesh

```
✅ Sequential: A → B → C → D → E (4 handoffs)
❌ Mesh: A↔B↔C↔D↔E (10 channels)
```

### Rule 4: ทุก New Agent ต้องมี Handoff Point

ก่อนเพิ่ม Agent ใหม่ ต้องตอบให้ได้:
- "Agent นี้รับงานจากใคร?"
- "Agent นี้ส่งงานให้ใคร?"
- "Agent นี้ใช้ Central Bus Field ไหน?"

---

## 10. ผลกระทบ

### เชิงบวก

| ผล | รายละเอียด |
|:---|:-----------|
| **ไม่มี Bottleneck** | Agent ส่งข้อมูลถึงกันโดยไม่ผ่าน Head ทุกครั้ง |
| **Pipeline Visible** | ทุกคนรู้ว่างานตอนนี้อยู่ที่ Stage ไหน |
| **Audit Ready** | ทุก Handoff มี timestamp + history |
| **Auto-Route** | งานส่งต่ออัตโนมัติเมื่อ Condition ครบ |
| **Scale ได้** | เพิ่ม Department → แค่เพิ่ม Field ใน Schema |

### เชิงลบ

| ผล | รายละเอียด |
|:---|:-----------|
| **ต้องเขียน Code Bus** | ต้องมี implementation ของ Shared JSON State |
| **Single Point of Failure** | ถ้า Bus ล้ม → ทั้ง Pipeline หยุด |
| **Schema แข็ง** | ถ้าต้องเพิ่ม Field ใหม่ → ต้อง Migrate Schema |

### การลดความเสี่ยง

| ความเสี่ยง | การป้องกัน |
|:----------|:-----------|
| Bus ล้ม | มี Fallback — Head คุยกันตรงได้ (โหมด degraded) |
| Schema not match | Validation Layer ทุกครั้งที่มี Input |
| Routing Rules ผิดพลาด | Head of Orchestration ตรวจสอบ + ทดสอบก่อน deploy |
| Agent เขียนทับข้อมูล | แยก department_state per department — Agent เขียนได้เฉพาะ department ตัวเอง |

---

## 11. แนวทางการ Implement

### ขั้นตอนการ Implement

| Phase | สิ่งที่ต้องทำ | ผู้รับผิดชอบ |
|:------|:------------|:------------|
| 1. Schema | สร้าง JSON Schema ตาม ADR-003 นี้ | Head of Orchestration |
| 2. Core Engine | สร้าง Central Bus Engine (อ่าน/เขียน/validate) | Engineering |
| 3. Routing Engine | สร้าง Workflow Routing Rules Engine | Orchestration + Engineering |
| 4. Notification | สร้าง Notification System แจ้ง Department Heads | Engineering |
| 5. Integration | เชื่อม Agent ทุกตัวกับ Bus | ทุก Department |
| 6. Testing | ทดสอบ Pipeline ปกติ + Exception Scenarios | QA + Orchestration |
| 7. AAR | After Action Review หลัง Implement | Head of Orchestration |

### ตัวเลือก Implementation

| วิธี | ข้อดี | ข้อเสีย |
|:----|:------|:--------|
| JSON File (Static) | ง่ายสุด, ไม่ต้องมี DB | ไม่ support concurrent writes |
| SQLite | ง่าย, persistent | Concurrent write อาจมีปัญหา |
| Redis/In-memory | เร็ว, concurrent OK | ไม่ persistent ถ้าไม่ตั้งค่า |
| Hermes Memory System | ใช้ระบบที่มีอยู่แล้ว | อาจช้าเมื่อ Scale |

---

## 12. อ้างอิง

| แหล่ง | เนื้อหา |
|:------|:--------|
| [ADR-001](./ADR-001-three-pillars-department-head.md) | 3 Pillars Foundation |
| [ADR-002](./ADR-002-two-tier-control-vs-data.md) | Two-Tier Architecture |
| [Profile #01](../profiles/01-head-of-orchestration.md) | Head of Orchestration Design |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | ภาพรวม Architecture |
| [google-ai-insights.md](../reference/google-ai-insights.md) | Data Schema + Protocol จาก Google AI |
| [ceo-hanuman-profile.md](../../.hermes/profiles/default/skills/ceo-hanuman-profile.md) | Pipeline Design Rules จาก CEO |

---

> ออกแบบตาม 3 Pillars + Two-Tier Architecture + Google AI Insights
> Schema + Protocol ใช้ JSON ตามที่ Google AI กำหนด
> สถานะ: ✅ Accepted — พร้อม Implement
