# Agent Activation System — Blueprint

> **เป้าหมาย:** ทำให้ 55+ Specialist Agents มีตัวตนจริง — CEO สั่งงานแล้วมีคนรับ ทำ ส่งผลกลับ
>
> Owner: Dr.solodev | CEO: เทอโบ | Status: Design

---

## ปัญหา

```
CEO: "@cfo-meetoo วางแผน budget"
  → Central Bus route ✅ → Queue ✅
  → cfo-meetoo รับ? ❌ ไม่มี agent ทำงานอยู่!
```

55+ specialists = SOUL.md profiles + Codex .toml files + OpenCode configs  
แต่ **ไม่มีตัวตน running** — ไม่มี process ไหนคอยรับ work จาก CEO

---

## แนวทาง: Incremental Activation

**ไม่ต้องเปิดพร้อมกัน 55 ตัว — เริ่มที่ 5 กรมหลักก่อน**

| Phase | Departments | Agents | มูลค่า |
|:-----:|:------------|:------:|:-------|
| **1** 🔴 | CFO, Architect, Engineering, Product, Orchestrator | 5 | CEO สั่งงานทีมได้แล้ว |
| **2** 🟠 | CMO, Design, QA, Sales, Support | +5 | ครบ front-facing |
| **3** 🟡 | Legal, Web3, Content, NetEng, CyberSec | +5 | ครบ support |
| **4** 🟢 | Psychology, UI, R&D, Specialists | +~40 | Full capacity |

---

## สถาปัตยกรรม

```
┌─────────────┐     สั่งงาน       ┌──────────────────┐
│   CEO       │ ────────────────→ │  Central Bus     │
│  (เทอโบ)    │                   │  (port 8099)     │
│             │ ←──────────────── │  /v1/observe     │
└─────────────┘   ผลลัพธ์กลับ      │  /v1/context     │
                                   └────────┬─────────┘
                                            │ route
                                            ▼
┌─────────────────────────────────────────────────────┐
│              Agent Worker Service                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ CFO Agent│ │Architect │ │Engineer  │ │Product │ │
│  │ (meetoo) │ │(songsak) │ │(changful)│ │(produck)│ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│         แต่ละ agent = script/worker ที่:               │
│         1. อ่าน SOUL.md → รู้บทบาท                     │
│         2. Poll queue → รับ work                      │
│         3. Execute task → ส่งผลกลับ                    │
└─────────────────────────────────────────────────────┘
```

### ทางเลือก Activation Method

| Method | ข้อดี | ข้อเสีย | เหมาะกับ |
|:-------|:------|:--------|:---------|
| **A. OpenCode Agent** | มี config แล้ว, ใช้ tool อะไรก็ได้ | ต้องเปิด session ค้างไว้, ไม่ autonomous | กรมหลัก (CEO สั่งผ่าน chat) |
| **B. Codex Agent** | 80 profiles พร้อม, autonomous .toml | ใช้ได้เฉพาะ Codex CLI | Specialist agents |
| **C. Python Worker** | ไม่พึ่ง platform, รันตลอด | ต้องเขียน worker เอง | Background queue consumer |
| **D. MCP Tool** | ใช้ได้ทุก platform | tool-based, ไม่ autonomous | Quick actions |

### แนะนำ: Hybrid (A + C)

```
Phase 1:
  - 5 กรมหลัก → OpenCode Agents (Method A)
    CEO @mention → agent รับงาน → แก้ไขไฟล์ → ส่งกลับ
  - Agent Worker Service (Method C)
    Poll Central Bus queue → execute → report

Phase 2+:
  - Specialist agents → Codex Agents (Method B)
  - MCP tools สำหรับ quick actions (Method D)
```

---

## Agent Worker Service Design (Method C)

```
worker/
├── main.py              # entry: poll queue → delegate
├── agents/
│   ├── base.py          # BaseAgent class
│   ├── cfo_agent.py     # CFO implementation
│   ├── architect_agent.py
│   └── ...
├── tools/               # tool implementations
├── queue.py             # Central Bus queue consumer
└── requirements.txt
```

### Worker Flow
```
1. Poll Central Bus /v1/context หรือ /v1/queue
2. รับ task → ตรวจ target_agent
3. Load agent profile (SOUL.md)
4. Execute ตามบทบาท
5. ส่งผลกลับผ่าน /v1/observe (source=agent, target=ceo-hanuman)
6. Log ไป brain/session-log.md
```

---

## Gap Analysis — สิ่งที่ต้องสร้าง

| Component | Status | ต้องทำอะไร |
|:----------|:------:|:-----------|
| SOUL.md profiles (55+) | ✅ มีแล้ว | แก้ให้ครบ |
| Codex .toml (80) | ✅ มีแล้ว | ทดสอบว่าใช้งานได้ |
| OpenCode agent configs | ⚠️ มีแค่ ceo-hanuman | เพิ่ม agent config สำหรับ 5 กรม |
| Central Bus queue | ✅ มีแล้ว | format ถูกต้อง |
| Agent Worker Service | ❌ ยังไม่มี | สร้าง worker ทั้งระบบ |
| Department API Keys | ❌ ยังไม่มี | สร้าง key per dept |
| Agent → CEO report back | ❌ ยังไม่มี | report flow |
| Cross-platform agent sync | ❌ ยังไม่มี | Codex agents → ทุก platform |

---

## Owner Decision Required

1. **Method**: Hybrid (A + C) หรือ Pure Python Worker?
2. **Phase 1 scope**: 5 กรม หรือขยาย?
3. **Timeline**: ทำต่อเนื่อง หรือรอให้ CEO Identity System เสร็จก่อน?
