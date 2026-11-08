# 🖥️ ใช้ SoloCorp OS บน OpenCode (สำหรับคน + agent ที่เปิดลิงก์มานี้)

> **10 วิ:** นี่คือระบบปฏิบัติการองค์กรสำหรับ AI — เปิด repo นี้ใน OpenCode แล้วคุยกับ CEO ได้เลย
> **10 sec (EN):** org-OS for AI agents. Open this repo in OpenCode and talk to the CEO.

## สำหรับคน (Human quickstart)

```bash
git clone https://github.com/Dr-SoloDev/Lab-solocorp-os2.4.git
cd Lab-solocorp-os2.4
opencode "@ceo-hanuman สวัสดี"
```

1. คุยกับ **CEO หนุมาน** ก่อนเสมอ — บอกงานภาษาคนได้เลย
2. งานใหญ่ → CEO จะแตกงานแล้วเปิด **ห้องแยกให้แต่ละแผนก** (ดูหัวข้อ multi-chat)
3. ไม่ต้องรู้คำสั่งเยอะ — เริ่มด้วย `/status` (ดูสุขภาพ) และ `/workspace` (เปิดห้องแผนก)

**อะไรใช้ได้เลย / อะไรต้องเปิด service ก่อน:**

| ใช้ได้ทันที ✅ | ต้องเปิด service ก่อน 🔌 |
|---|---|
| คุย วางแผน `/workspace` เปิดห้องแผนก | Central Bus (`:8099`) — งานผ่านคิว/bus |
| อ่าน profiles/rules ทั้งหมด | MCP server — skills ขั้นสูง |
| `/handoff` `/audit` (ระดับเอกสาร) | `/triage` `/mirror` `/orchestrate` (ต้องมี workers+bus) |

## สำหรับ agent (ที่ถูกโยนลิงก์ repo นี้มาให้อ่าน)

อ่านตามลำดับนี้ (อย่าข้าม):
1. `AGENTS.md` — กติกาห้องเครื่อง (hierarchy, session, safety, test)
2. `rules/INDEX.md` — พฤติกรรม 6 ไฟล์ (30 วินาที)
3. `profiles/INDEX.md` — สารบบแผนก (ใครทำอะไร)
4. งานที่ได้รับมอบ — ทำใน branch ใหม่ ส่งหลักฐาน ไม่แตะ `main` ตรง

ข้อตกลง:
- ภาษาไทยก่อน (technical terms ภาษาอังกฤษได้)
- Head ไม่ลงมือเอง — delegate ให้ specialist
- รายงานกลับแบบ: สรุป + ไฟล์ที่แตะ + ติดขัด + ส่งต่อให้ใคร
- ห้าม commit `.env` / ไฟล์ runtime (`*.db-shm`, `*.db-wal`, logs)

## 🏢 Multi-chat: 1 แผนก = 1 ห้อง (`/workspace`)

**Manual (คนเปิด):** เปิดแชทใหม่ ตั้งชื่อแท็บ `[แผนก]+งาน` วาง context bundle
**Autonomous (ระบบเปิดเอง — พิสูจน์แล้ว):**
`opencode run --agent <slug> --title "[แผนก] งาน" --format json "<bundle>"`
(รันใน repo root · ตามงาน `session list` · เก็บ `export` · ปิด `session delete`)

แทน subagent ภายนอก — เปิดแชทใหม่ใน OpenCode Desktop ตั้งชื่อแท็บ `[แผนก]+งาน`:

```
/workspace [แผนก] [งาน]     เช่น /workspace ช่างฟูล แก้บั๊กตาชั่ง
```

skill `skills/@solocorp/cross-dept/dept-workspace/SKILL.md` จะประกอบ
context bundle (ตัวตน+งาน+บริบท+กติกาส่งกลับ) ให้ — ก็อปไปวางในแชทใหม่ได้เลย

## 🌱 Fork ไปปรับใช้ (หนึ่งแกน หลายตัวตน)

- เปลี่ยนชื่อ/นิสัยแผนกได้อิสระที่ `profiles/*/SOUL.md` แล้วรัน `/deploy full`
- อย่าแตะสัญญา core: โครง SOUL 5-layer, `rules/` behavior, API bus (ดู `docs/ARCHITECTURE.md`)
- อยากเริ่มเบาๆ: ดู starter pack 12 แผนก + `rename.py` (ถาม-ตอบ 25 ข้อได้บริษัทชื่อตัวเอง)
- เจอหลักการก่อนแตะอะไร: `PRINCIPLES.md` ⚖️
