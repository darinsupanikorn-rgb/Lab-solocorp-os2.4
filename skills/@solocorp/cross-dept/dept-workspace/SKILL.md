---
name: "@solocorp/cross-dept/dept-workspace"
version: 0.1.0
category: cross-dept
platforms: [opencode]
trigger: "/workspace"
mirror_check: L1
---

# 🏢 Dept Workspace — เปิดห้องทำงานให้แผนก (2 โหมด)

> 1 แผนก = 1 ห้อง พร้อมตัวตน + บริบท + งาน
> - **Manual:** คนเปิดแชทใหม่เอง (ดูแล้วรู้ว่าใครทำอะไร — เหมาะกับ OpenCode Desktop)
> - **Autonomous:** CEO/ทีมเปิดห้องเองผ่าน CLI (ไม่ต้องรอคน — พิสูจน์แล้วว่าใช้ได้จริง)

## Purpose
เมื่อ Owner สั่งว่า "ให้ [แผนก] ทำ [งาน]" — แทนที่จะคุยปนในแชท CEO,
เปิดห้องแยกให้แผนกนั้น พร้อมความจำและบริบทที่ต้องใช้ ไม่มีเกิน ไม่มีขาด

## Inputs
| Field | Required | Description |
|:------|:--------:|:------------|
| `department` | Yes | ชื่อแผนก (ceo, coo, architect, engineering, design, qa, ฯลฯ — ดู `profiles/INDEX.md`) |
| `task` | Yes | งานที่จะให้ทำ (1 งานต่อ 1 ห้อง — ไม่ยัดหลายงาน) |
| `context` | No | บริบทเพิ่มเติม (ไฟล์ที่เกี่ยวข้อง, ข้อจำกัด, ผลจากแผนกก่อนหน้า) |

## Steps — Manual mode (คนเปิดห้องเอง)
1. เปิด `profiles/INDEX.md` หา SOUL path ของแผนก
2. ประกอบ **context bundle** (ด้านล่าง) — ยาวไม่เกิน 60 บรรทัด
3. เปิดแชทใหม่ใน OpenCode → ตั้งชื่อแท็บ `[แผนก] + งานสั้นๆ` (เช่น `[ช่างฟูล] แก้บั๊กตาชั่ง`)
4. วาง context bundle เป็นข้อความแรก → เริ่มทำงานในห้องนั้น
5. จบงาน → เอา **รายงานกลับ** (ด้านล่าง) มาวางในแชท CEO

## Context Bundle (template — ก็อปแล้วเติม)
```
🏢 ห้องทำงาน: [ชื่อแผนก] ([หัวหน้า])
📄 ตัวตน: อ่าน profiles/[NN-name]/SOUL.md แล้วทำตาม (นิสัย+หน้าที่+ขอบเขต)
🎯 งาน: [งาน 1 อย่าง ชัดๆ]
📦 บริบท: [ไฟล์/เงื่อนไข/ผลจากงานก่อน — เฉพาะที่ต้องใช้]
📏 กฎ: rules/INDEX.md → เปิดไฟล์ behavior ที่ตรงงาน
✅ ส่งกลับ: สรุป + ไฟล์ที่แตะ + ติดขัด + สิ่งที่แผนกต่อไปต้องรู้
```

## รายงานกลับ (template)
```
✅ [แผนก] เสร็จ: [สรุป 1-3 บรรทัด]
📁 แตะไฟล์: [list]
⚠️ ติดขัด: [หรือ "ไม่มี"]
➡️ ส่งต่อ: [แผนกต่อไปต้องรู้อะไร]
```

## Steps — Autonomous mode (CEO/ทีมเปิดห้องเอง ไม่รอคน)

> พิสูจน์แล้ว (smoke test ผ่าน, sessionID ออก): bode นี้ใช้ `opencode run` เปิดห้อง headless

```bash
cd /data/projects/Lab-solocorp-os2.4   # ต้องรันใน repo (ห้าม /tmp — FileSystem กัน)
opencode run --agent <slug> --title "[แผนก] งานสั้นๆ" --format json "<context bundle + task>"
```

- `--agent` = slug จากตารางด้านล่าง (`opencode agent list` ดูทั้งหมด)
- `--title` = ชื่อห้อง (โผล่ใน Desktop เป็นแท็บ — ผู้ใช้เห็นว่าใครทำอะไร)
- `--format json` = ได้ sessionID กลับมา → ตามงานด้วย `opencode session list`
- เก็บบันทึก: `opencode export <sessionID>` · ปิดห้อง: `opencode session delete <sessionID>`
- งานยาวครอบด้วย `timeout <วินาที> opencode run ...` กันค้าง

### Agent slug map (dept → --agent)
`ceo-hanuman, qa, architect-songsak, engineering-changful, design-kreet, ui-designer,
orchestrator-wut, product-produck, content-creator-sek, cfo-meetoo, cmo-mark,
sales, support, legal-tulya, web3-aywa, cron-pipeline, monitor-watchdog,
exception-triage, pipeline-auditor, routing-config-agent, mcp-builder`
- แผนกที่ไม่มี slug (coo, psychology, game-dev) → ไม่ต้องใส่ `--agent`
  (bundle มี SOUL path อยู่แล้ว agent หลักอ่านเอง)

### กติกาห้อง autonomous (ทุกทีมต้องรู้)
- ห้องที่ spawn มาสืบทอด permission จาก `opencode.json` (ask/deny ยังบังคับ) — ปลอดภัยเท่าแชทคน
- **ห้อง headless เจอ `ask` = ถูก auto-reject ทันที** (ไม่มีคนกด) → ใน bundle ต้องสั่งชัด:
  `อ่านไฟล์ด้วย Read/Glob/Grep เท่านั้น ห้ามใช้ bash เปิดไฟล์/pipe/redirect`
- 1 ห้อง = 1 งานเหมือน manual · CEO ถือ sessionID ทุกห้อง · เสร็จแล้ว delete ปิดห้อง
- ค่าใช้จ่าย: เปิด 1 ห้องโหลด context ทั้ง repo (~50k tokens) — รวมงานต่อห้อง อย่าเปิดพร่ำเพรื่อ

## Rules
- 1 ห้อง = 1 แผนก + 1 งาน — ห้ามคุยข้ามแผนกในห้องเดียวกัน (คุยผ่าน CEO เท่านั้น)
- ความจำอยู่ในไฟล์ (`session-log.md`, handoff) ไม่ใช่ในประวัติแชท — ห้องใหม่เริ่มได้เสมอ
- งาน L5 (vision/org) ห้ามมอบ — กลับมาถาม Owner
- ชื่อแท็บต้องบอกได้ว่า "ใครกำลังทำอะไร" — เปิดดูแท็บแล้วรู้ทันที
