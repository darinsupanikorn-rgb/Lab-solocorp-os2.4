# MCP Department Servers — Content Creator Pilot

> **สถานะ ณ 2026-11-01:** เอกสารนี้เก็บ implementation และ verification history ของ Content Creator MCP pilot. ใช้ [`docs/prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md`](../prds/PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md) เป็น roadmap ปัจจุบันสำหรับ SoloCorp App. Pilot นี้ยังไม่ใช่ first-party app, module registry, หรือหลักฐานว่าทุก MCP client ผ่าน end-to-end. Codex และ Perch workflow มีหลักฐานในบันทึกด้านล่าง; OpenCode E2E ยังมีข้อจำกัดตามบันทึกเดิม.

ข้อกำหนดที่ยังใช้ต่อ: Content Creator MCP ต้องคงการใช้งานแบบ standalone และ client-managed model. งาน MVP ถัดไปคือเชื่อม pilot นี้เข้ากับ local app/registry/task history; การสร้าง LLM ภายใน department server ไม่ใช่เงื่อนไขเริ่ม MVP.

## เป้าหมาย

สร้างรูปแบบที่ผู้ใช้เลือกเสียบ MCP server เฉพาะแผนกที่ต้องการได้ทันที โดยแต่ละ server มีหัวหน้าเป็นประตูรับงานและซ่อนรายละเอียดการทำงานของ specialist ไว้ภายในแผนก

ระยะนำร่องนี้ครอบคลุมสองชิ้น:

1. `central-bus` — MCP infrastructure สำหรับจัดเก็บและอ่าน payload ของแผนก
2. `content-creator` — MCP department server ของเสก สำหรับสร้างร่างคอนเทนต์ สคริปต์วิดีโอ visual prompt และตรวจ Publish Gate

## Client-managed LLM และ provenance

ใน workflow ปกติ OpenCode, Codex หรือ Local AI เป็นผู้เลือก provider/model และสร้างเนื้อหาเอง ส่วน MCP รับเนื้อหาที่สร้างเสร็จแล้วเพื่อจัดเก็บ versioning ผูก campaign เก็บ source references และตรวจ Publish Gate เท่านั้น เส้นทาง ingestion นี้ไม่เรียก `workers/llm_provider.py` และห้ามส่ง API key หรือ credential เข้า MCP

เครื่องมือ `ingest_client_generated_artifact` รับ `campaign_id`, `artifact_type`, `content`, `source_references` และ `provenance` (`client`, `provider`, `model`) โดย client/provider/model เป็นข้อมูลที่ผู้เรียกแจ้งเอง ไม่ได้พิสูจน์ตัวตนหรือยืนยันการใช้โมเดลจริง ระบบบันทึก `lifecycle_state: client_generated` และ `provenance_status: client_supplied_unverified`; ค่านี้ต้องไม่ถูกนำเสนอเป็น provenance ที่ผ่านการรับรอง `save_human_edited_artifact` ยังคงใช้เฉพาะงานที่มนุษย์แก้ไข

```text
OpenCode / Codex / Local AI เลือก LLM และสร้างเนื้อหา
        │
        ▼
ingest_client_generated_artifact
        │ campaign + artifact + references + self-reported provenance
        ▼
Central Bus Store → versioned campaign manifest → review_publish_gate
                                                   │
                                                   └→ review required; no auto-publish
```

หากต้องใช้ LLM ฝั่ง background ในอนาคต ให้เป็น adapter เสริมที่ตั้ง provider/model และ credential ใน local config อย่างชัดเจน ห้าม fallback หรือสลับโมเดลโดยเงียบ

## สถาปัตยกรรม

```text
OpenCode V2 / Codex
        │ เลือกต่อ MCP server ที่ต้องการ
        ├── central-bus       (โครงสร้างข้อมูลกลาง)
        └── content-creator   (หัวหน้าเสก → specialist ภายใน)
                                  │
                                  └── shared bus store
                                      central_bus/content/
```

`bus_store.py` เป็น domain-neutral library ที่ทั้งสอง server ใช้ร่วมกัน ส่วน MCP เป็น protocol adapter เท่านั้น จึงไม่ผูก business logic กับ client รายใดรายหนึ่ง

## ขอบเขต Content Creator

- หัวหน้าแผนก: เสก (Content Creation)
- specialist ภายใน: Copywriter, Visual Creator, Video Editor, Trend Scout
- tools ที่เปิดให้ client เรียกผ่านหัวหน้า:
  - `content_department_info`
  - `create_content_draft`
  - `create_video_script`
  - `design_visual_prompt`
  - `review_publish_gate`
- resource: `solocorp://content/sop`

ทุก output เป็นไฟล์ใน `central_bus/content/` และคืน JSON สรุปผลกับ path ของ artifact เพื่อควบคุมขนาด context

## เกณฑ์ผ่าน

- [x] มี shared bus store พร้อม path guard และ atomic write
- [x] Central Bus MCP ลงทะเบียน tools `submit`, `fetch`, `list`
- [x] Content Creator MCP ลงทะเบียน tools และ SOP resource
- [x] Publish Gate ตรวจ redaction + R1–R5 และไม่เผยแพร่อัตโนมัติ
- [x] OpenCode config ต่อได้ทั้งสอง server
- [x] Codex config ต่อได้ทั้งสอง server
- [x] มี unit tests สำหรับ storage, path safety และ content tools
- [x] ทดสอบ stdio handshake จริงจาก MCP client ใน environment นี้
- [x] เพิ่ม ingestion สำหรับ client-generated artifact พร้อม lifecycle state และ provenance ที่ระบุว่า unverified
- [x] Publish Gate แสดง provenance แบบ self-reported และคง human approval gate

## วงรอบตรวจสอบ

หลังแต่ละรอบให้ตรวจตามลำดับ: import → unit tests → server tool listing → stdio smoke test → ตรวจ `git diff` และสถานะไฟล์ที่สร้างใน bus

## Source audit ของ Content Creator

- `profiles/15-content-creator/SOUL.md` สืบมาจาก commit `3be15da` และมีการขยายตัวตน/ภารกิจใน `5d2e74b`; working tree เดิมสะอาด จึงไม่ต้อง rollback
- `workers/agents/content_agent.py` เริ่มใน `53cae41` และมีการแก้ edge case ของ input เสียใน `9815824`; เก็บเวอร์ชันปัจจุบันไว้เพราะมี test รองรับ แม้ hash จะต่างจาก D2 snapshot เดิม
- `solocorp_skills/creator.py` เป็นกติกา Creator Kit เดิม และ `solocorp_skills/redact.py` เป็นแหล่ง Publish Gate; Content MCP เรียกใช้ gate เดิมแทนการสร้างกฎซ้ำ

## Verification record

- Targeted MCP + Content tests: **11 passed**
- Full suite: **959 passed, 123 warnings**
- Auto-QA gate: **PASS**, coverage **75.4%** (threshold 9%)
- OpenCode `mcp list --pure`: `central-bus` และ `content-creator` = **connected**
- Codex `mcp list --json`: ลงทะเบียน `central-bus` และ `content-creator` = **enabled**

## Verification — 2026-10-30

- Targeted tests: `tests/test_content_mcp.py` และ `tests/test_mcp_stdio.py` ผ่าน **22 tests**; stdio smoke เรียก ingestion และ Publish Gate ด้วย artifact สังเคราะห์
- OpenCode แสดง `content-creator` = **connected**; client-native call ยังไม่ถึง MCP tool: ชื่อ model ใน agent config ไม่อยู่ในรายการ CLI และ model ที่ CLI แสดงตอบ HTTP 402 ก่อนการเรียก tool
- OpenCode Phase 2 attempt (2026-10-30): ตั้ง project `ceo-hanuman` เป็น `opencode/beam-free` ซึ่ง CLI แสดงว่า active, รองรับ tool call และมีค่า input/output ที่แสดงเป็น 0 (ยังไม่ยืนยันโควตาหรือความพร้อมใช้งานจริง); การรัน synthetic campaign `campaign_synth_opencode_02` หนึ่งครั้งหยุดก่อน MCP ด้วย HTTP 400 `unsupported_parameter`: endpoint ปฏิเสธ `agents_md` ว่าเป็น argument ที่ไม่รู้จัก
- ตรวจหลังความล้มเหลวแล้วไม่พบ artifact, manifest หรือ Gate report ของ `campaign_synth_opencode_02`; ไม่มี MCP tool ถูกเรียก จึงไม่ถือว่า OpenCode E2E ผ่าน
- ปรับ project config ให้ OpenCode Desktop เป็นผู้เลือก model ต่อ session: เอา model override ออกจาก `ceo-hanuman` และไม่มี root `model` pin; provider/model ที่เลือกต้องเชื่อมต่อและพร้อมใช้ใน project ก่อน
- Codex client E2E: **PASS สำหรับการเรียก tool และบันทึกผล** ผ่าน interactive Codex CLI `0.165.0` ด้วย session override `on-request`; อนุมัติ ingestion และ gate แยกเป็นรายครั้ง โดยไม่เปลี่ยน global config
- Codex synthetic campaign `campaign_synth_codex_01`: artifact `campaign-campaign_synth_codex_01-client-generated-article-ee9197_20261029T180200284565Z.md`; manifest `campaign-campaign_synth_codex_01-manifest_20261029T180215964471Z.json`; report `campaign-campaign_synth_codex_01-publish-gate-v1_20261029T180215910413Z.md`
- ตรวจ manifest แล้ว: asset เป็น `client_generated`, provenance เป็น `client_supplied_unverified`, Publish Gate เป็น `review_required`, `gate_passed=false`; ไม่มีการ Publish ซึ่งเป็นผลที่คาดหวังสำหรับเนื้อหาสังเคราะห์ที่ไม่ผ่าน R1–R5
- Codex ใช้ model `gpt-6-luna` ผ่าน provider `maxplus` ตาม config ปัจจุบัน; CLI ยืนยัน credential ถูกตั้งค่าแต่ไม่แสดงยอดโควตาคงเหลือ การเรียกครั้งนี้สำเร็จ แต่ยอดคงเหลือยังไม่ได้รับการยืนยัน; usage ที่ CLI รายงานคือ 42,463 input + 79,949 cached input และ 1,002 output tokens
- End-to-end ผ่านทั้งสอง client ยัง **pending**: Codex tool workflow ผ่าน; OpenCode ยังไม่ถึง MCP tool เพราะ OpenCode API ปฏิเสธ request ของ `opencode/beam-free` ด้วย HTTP 400; ยังต้องทดสอบ model ที่เลือกจาก Desktop UI

## Verification — 2026-10-30 (รอบที่ 2: full workflow จาก client ที่สาม)

- Client ที่สาม (Perch Desktop) รัน workflow ครบวงจรผ่าน: สร้างเนื้อหา (client-managed LLM) → `ingest_client_generated_artifact` → `review_publish_gate` → แก้ตาม feedback → ingest ใหม่ → `record_human_approval`
- Loop การแก้ซ้ำพิสูจน์แล้ว: v1 ถูก gate ปฏิเสธ (ขาด R1 หลักฐาน + R3 calibration) → v3 ผ่าน R1–R5 และ redaction ครบ (campaign `campaign_mcp_pilot_llm_02`); หลักฐาน R1 ต้องอยู่ในรูปแบบที่ `_EVIDENCE_RE` รู้จัก เช่น `tests/*.py`, git sha, `bus/*.json`, ADR
- Full workflow สมบูรณ์ที่ `campaign_mcp_pilot_llm_04` (v4): article + visual prompt + video script + audio cue sheet ครบ dependency, redaction สะอาด, R1–R5 ผ่าน; approved ด้วย human approval ที่ override `source verification` + `media rights` พร้อม note ใน audit record
- **Bug ที่พบและแก้แล้ว**: template visual prompt ใน `content_service.py` เดิมเขียน "Do not invent logos, customer data, or claims" แล้วคำว่า "customer data" โดน FLAG pattern CUSTOMER ของ `solocorp_skills/redact.py` จับเป็น PII — scaffold ที่ระบบสร้างเองยิง gate ตัวเอง แก้เป็น "personal data" แล้ว targeted tests ผ่าน 31/31 (`tests/test_content_mcp.py` + `tests/test_mcp_stdio.py`)
- **ข้อจำกัดที่พบ**: MCP server process แคชโค้ดเก่าหลังแก้ template — ต้อง restart server จึงเห็น fix; ชั่วคราวใช้ direct service call ยืนยันว่า fix ถูกต้อง
- **Design flaw ที่ควรแก้ต่อ (เปิด issue)**: (1) asset ที่เข้า campaign แล้วลบ/แทนที่ไม่ได้ผ่าน MCP และ gate รวม redaction จากทุก asset ตลอดกาล เนื้อหาพังหนึ่งชิ้นดึงทั้ง campaign ลง — ทางแก้ปัจจุบันคือเปิด campaign ใหม่; ควรมี asset removal หรือ redaction ต่อ asset version (2) ควรมี interactive approval prompt (เช่น MCP elicitation) ให้ระบบเด้งคำถามอนุมัติกลับมาที่มนุษย์โดยตรง แทนการให้ agent พิมพ์ `approver_note` แทน
- สรุป: ขั้น "ทดสอบ workflow Content Creator จริง" จาก checkpoint ปิดแล้ว; เหลือ LLM generation ฝั่ง background (adapter เสริมตามข้อกำหนด client-managed) และ OpenCode E2E ที่ยังติด HTTP 400
