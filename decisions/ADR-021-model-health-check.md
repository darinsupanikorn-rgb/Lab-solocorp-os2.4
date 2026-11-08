# ADR-021: Model Health Check — กัน LLM chain ตายเงียบ

**วันที่:** 2026-10-20
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — Owner สั่ง "model health check ใน watchdog (กันตายซ้ำ)")
**ต่อยอด:** ADR-019 (ซ่อม dispatch path — เจอปัญหานี้ระหว่างทำ)

---

## บริบท

ระหว่างซ่อม F1+F2 พบว่า **LLM fallback chain ใช้ชื่อโมเดลที่ไม่มีจริง 2 ตัว**
(`muse-spark-1.3-contributor-free`, `space-bunny-free`) → ทุกโมเดลคืน
"Model not found" → agent 19 ตัว **"ตาบอด"**

แต่สิ่งที่ทำให้มันอันตรายกว่า fail ปกติคือ **ไม่มี error ชัดเจน**:
pipeline ยังรายงาน `status: completed` → evidence ถูกเขียน → AAR ถูกเขียน →
task ถูกทำเครื่องหมายว่าสำเร็จ → report ถูกส่ง CEO
→ **ไม่มีใครรู้ว่า 19 agent ไม่ได้คิดอะไรเลย**

แก้ชั่วคราวแล้ว (เปลี่ยนชื่อโมเดล) แต่**ไม่ได้แก้ต้นเหตุ** — opencode เปลี่ยนชื่อ/ลบโมเดลฟรี
ไปเรื่อย ๆ → ปัญหานี้จะกลับมา

---

## การตัดสินใจ

### 1. ตรวจชื่อโมเดลอัตโนมัติ ใน watchdog
```
watchdog (cron ทุก 5 นาที)
  └─ check_model_health()
       └─ audit_models()
            ├─ เทียบ MODEL_FALLBACKS กับ `opencode models` (จริง)
            ├─ missing = โมเดลใน chain ที่ไม่มีจริง   → 🚨 เตือน
            ├─ usable  = โมเดลใน chain ที่ใช้ได้
            └─ candidates = โมเดลใหม่ที่ยังไม่อยู่ใน chain → 💡 ข้อเสนอ
```

### 2. เตือน CEO ผ่านทางเดิมของระบบ
watchdog → `POST /v1/observe` (action=`report_back`) → bus เขียน `ceo_alerts` + ปิดสถานะ
→ ไม่ต้องสร้างช่องทางแจ้งเตือนใหม่ (ใช้ของเดิมจาก ADR-019)

### 3. Cache 6 ชั่วโมง
`opencode models` ใช้ ~4 วินาที → watchdog ทุก 5 นาทีไม่ควรเรียกทุกครั้ง
→ cache ที่ `bus/system/model_health.json` (gitignored) · TTL 6 ชม.

### 4. แยก "ตรวจชื่อ" ออกจาก "ทดสอบจริง"
| โหมด | ใช้เมื่อ | ต้นทุน |
|:--|:--|:--|
| ตรวจชื่อ (default) | watchdog ทุก 5 นาที | ~4 วิ (cache) |
| `--verify <model>` | ก่อนเพิ่มโมเดลใหม่ | ~15–45 วิ + LLM call |
| `--verify-all` | ตรวจ chain ทั้งชุด | ~2–5 นาที |
| `--candidates` | หาโมเดลใหม่ที่ใช้ได้ | ~2–5 นาที |

**สำคัญ:** `--verify` ต้องรัน **cwd = repo root** เพราะนั่นคือเงื่อนไขจริงที่ทำให้ `agents_md` error
→ ตัวช่วยจำลองวิธีเดียวกับ llm_provider เป๊ะ

---

## ผลกระทบ

**✅ ดี**
- โมเดลหาย → เตือนภายใน **6 ชั่วโมง** (ไม่ใช่เมื่อมีคนเจอ)
- เตือน CEO ผ่าน `ceo_alerts` (severity HIGH) → มองเห็นใน dashboard
- watchdog exit 1 → cron log เห็นเป็น error
- เจอโมเดลใหม่ที่ใช้ได้ 2 ตัว (`nemotron-3-ultra-free`, `big-pickle`) → เพิ่มเข้า chain แล้ว
  chain เดิมมี 5 → **ตอนนี้ 7 โมเดล**

**⚠️ ต้องรู้**
- ตรวจแค่ **ชื่อ** — ไม่ได้ยืนยันว่าโมเดลคิดได้จริง (โมเดลอาจมีแต่ใช้ไม่ได้เพราะ `agents_md`)
  → `--verify` คือคำตอบ · แต่ต้องเรียกเอง
- cache 6 ชม. = ช่วงที่โมเดลอาจหายโดยยังไม่เตือน
- ยังไม่ได้แก้ `agents_md` ต้นเหตุ — แก้ที่ระดับชื่อโมเดลแทน
  (ถ้าโมเดลที่ใช้ได้ทั้งชุดโดน agents_md → จะตายอีก แต่ตอนนี้มี monitor เตือน)

---

## หลักฐาน

- ตรวจชื่อ: chain 5/5 ปกติ
- **จำลองเส้นทางตาย:** ใส่โมเดลปลอม 2 ตัว → `[WARN]` + `exit 1` +
  `ceo_alerts` ได้ `HIGH` พร้อมรายการ missing ✅
- `--candidates` ทดสอบจริง → เจอ `nemotron-3-ultra-free` + `big-pickle` ใช้ได้ → เพิ่มเข้า chain
- เทสต์: `tests/test_model_health.py` — **19/19 ผ่าน**
