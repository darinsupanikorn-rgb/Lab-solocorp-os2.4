# 💰 Token / Quota Accounting

> **incident 2026-10-25** — โควตาฟรีของ workspace หมดกลางวันโดยไม่มีใครรู้ล่วงหน้า
> 297 requests สำเร็จ แล้วอีก **186 requests ถูกยิงเข้ากำแพง 429 เปล่า ๆ**
> เอกสารนี้อธิบายว่าวัดอะไร จากไหน และทำไมตัวเลข "15.2M tokens" ที่เห็นใน console
> ไม่ใช่สิ่งที่เราคิดตอนแรก

---

## 1. อ่านตัวเลขให้ถูกก่อน (แก้ความเข้าใจผิด)

Console แสดงตาราง model แบบนี้:

```
DeepSeek V4.1 Flash   270   779.5k   15.2M   -   186.9k   $0.00
```

คอลัมน์คือ: `requests | input | cache_read | cache_write | output | cost`

| อ่านผิด (ตอนแรก) | อ่านถูก |
|:--|:--|
| "15.2M output tokens → ~56k ต่อคำขอ → โมเดลตอบยาวเกิน" | **15.2M = cache_read** (บริบทถูกอ่านซ้ำทุก step) · **output จริง = 186.9k** |

ตรวจกับ export จริงของ console (`request-logs-2026-10-25.json`, 488 records):

| | deepseek-v4.1-flash-free | ทั้ง workspace |
|:--|--:|--:|
| requests (สำเร็จ) | 271 | 298 |
| input | 812,295 | 1,167,820 |
| **cache_read** | **15,431,680** | **15,640,374** |
| cache_write | 0 | 0 |
| output | 188,132 | 195,302 |
| reasoning | 76,023 | 79,495 |
| cost (รายงาน) | $0.00 | $0.00 |
| **paid-equivalent** ที่ราคา `deepseek-v4.1-flash` ($0.3/$0.006/$1.2 per M) | **≈ $0.56** | — |

**บทเรียน:** cache read ถูกมาก ($0.006/M → 15.4M = $0.09) ตัวที่แพงคือ output
($1.2/M) และ input ($0.3/M) — ดู `cost` ไม่ใช่ดู token ก้อนใหญ่สุด

### แล้วอะไรทำให้โควตาหมด

| หลักฐาน | แปลว่า |
|:--|:--|
| 169 × HTTP 429 `FreeUsageLimitError` | โควตาฟรีมีเพดาน **จำนวน request/วัน** (ตายที่ ~300) |
| 19 × HTTP 403 `upstream_stream_incomplete` | ช่องทาง google (custom connection) มีปัญหาแยกต่างหาก |
| 2 × HTTP 402 `Insufficient account funds` | กระเป๋า Console = $0 → โมเดลเสียเงินใช้ไม่ได้ |
| 186 × outcome=`rejected` | **ของเสียที่ป้องกันได้** — retry เข้ากำแพงหลังโควตาตายแล้ว |

ตัวที่เผาโควตาไม่ใช่ agent ตัวใดตัวหนึ่ง แต่เป็น **session ของ CEO เอง**:
188 requests / 151k output ใน session เดียว (78% ของ output ทั้งวัน)

---

## 2. ข้อมูล usage มาจากไหน (แหล่งความจริง)

`~/.local/share/opencode/opencode.db` → ตาราง `session_message` (`type='assistant'`)

```json
{
  "time": {"created": 1792909301388, "completed": 1792909305562},
  "agent": "ceo-hanuman",
  "model": {"id": "deepseek-v4.1-flash-free", "providerID": "opencode"},
  "finish": "tool-calls",
  "cost": 0,
  "tokens": {
    "input": 128, "output": 331, "reasoning": 0,
    "cache": {"read": 79360, "write": 0}
  }
}
```

ข้อดี: ตรงกับที่ gateway คิดเงิน (ตรวจกับ export แล้ว), ครอบคลุมทุก session
(desktop + CLI), ไม่ต้อง parse stdout, ไม่ต้องพึ่ง console

### ทำไมทุก call ต้องมี session id ของเราเอง

`llm_provider` ส่ง `--session ses_llm<hex>` เองทุกครั้ง → ได้ 3 อย่าง:
1. อ่าน usage ของ call นั้นได้ตรงตัว (ไม่ชนกับ session อื่นที่รันขนานกัน 3 ตัว)
2. join กับ console request logs ได้ด้วย `sessionID`
3. ไม่เปลี่ยนพฤติกรรมเดิม — `opencode run` สร้าง session ใหม่ทุกครั้งอยู่แล้ว

---

## 3. สถาปัตยกรรม 3 ชั้น

```
think()
  │
  ├─ 1) quota lock?  ── locked ──► คืนทันที (~1 ms) ไม่ยิง LLM
  ├─ 2) งบรายวัน?    ── เกิน  ──► คืนทันที + บอกว่าชนเพดานไหน
  │
  ├─ ยิง LLM (1 session ต่อ 1 attempt)
  │
  ├─ 3) อ่าน usage จาก DB → เขียน ledger 1 บรรทัด (สำเร็จ/ล้ม ก็เขียน)
  │
  └─ เจอ 429/402? → lock_quota(until) → หยุดทั้ง chain (ไม่ไล่ 5 โมเดล × 3 retry)
```

| ไฟล์ | บทบาท |
|:--|:--|
| `workers/token_ledger.py` | อ่าน usage / ledger / เพดาน / lock / แกะ `retryAfterMs` |
| `bus/system/token-ledger.jsonl` | runtime — 1 บรรทัดต่อ call (gitignored) |
| `bus/system/llm_quota.json` | runtime — เวลาปลดล็อก (gitignored) |
| `scripts/token-report.py` | รายงาน: ledger vs DB, top sessions, สถานะงบ |

### ledger entry

```json
{"agent":"content-creator-sek","model":"opencode/deepseek-v4.1-flash-free",
 "session_id":"ses_llm9abd1ecc80fc40e8afef","ok":true,"duration_ms":15100,
 "prompt_chars":1240,"result_chars":500,"error":"",
 "requests":1,"input":140,"output":471,"reasoning":814,
 "cache_read":60784,"cache_write":0,"cost":0.0,
 "ts":"2026-10-25T13:31:46+07:00"}
```

`requests` นับเฉพาะแถวที่มี token จริง; request ที่ถูกปฏิเสธนับเป็น `failed`
(ยังอยู่ใน ledger เพื่อตรวจย้อนหลัง แต่ **ไม่กินงบ**)

---

## 4. Env

| ตัวแปร | ค่าเริ่มต้น | ความหมาย |
|:--|--:|:--|
| `SOLOCORP_LLM_DAILY_REQUESTS` | 400 | เพดาน request/วัน (เกิน = ไม่ยิง) |
| `SOLOCORP_LLM_WARN_REQUESTS` | 200 | เริ่มเตือนใน log |
| `SOLOCORP_LLM_DAILY_OUTPUT_TOKENS` | 2,000,000 | กัน runaway |
| `SOLOCORP_LLM_DAILY_COST_USD` | 1.00 | กันค่าเงิน (ฟรี = $0 จึงไม่ทริกเกอร์) |
| `SOLOCORP_LLM_LOCK_DEFAULT_S` | 3600 | ระยะล็อกเมื่อ error ไม่บอกเวลา reset |
| `SOLOCORP_TOKEN_LEDGER` / `SOLOCORP_LLM_QUOTA` / `OPENCODE_DB` | — | override path (เทสต์ใช้) |
| `SOLOCORP_AGENT_NAME` | `unknown` | ชื่อ agent ใน ledger ถ้า caller ไม่ส่ง `agent=` |

> เพดาน 400 ตั้งจากข้อมูลจริง: free tier ตายที่ ~297 สำเร็จ/วัน
> 400 จึงกัน **runaway loop** ไม่ใช่กัน free limit (อันนั้น 429 lock จัดการ)

---

## 5. ใช้งาน

```bash
# วันนี้ทั้ง org (รวม session ของ CEO ที่ไม่ได้ผ่าน workers)
python scripts/token-report.py --sessions 5

# ดูสถานะล็อก / ปลดล็อกด้วยมือหลัง Owner เติมเงิน
python -c "from workers import token_ledger as t; print(t.quota_status())"
python -c "from workers import token_ledger as t; t.clear_quota()"
```

`think()` คืน `⚠️ LLM ไม่พร้อม: ...` (ไม่ raise) เมื่อถูกล็อก/เกินงบ — agent
ทุกตัวจึงได้ข้อความที่อธิบาย root cause แทนการรอ timeout

---

## 6. ข้อจำกัดที่รู้ตัว

| ข้อจำกัด | ผลกระทบ | ทางแก้ |
|:--|:--|:--|
| ledger เก็บเฉพาะ call ที่ `workers/` ยิง | ไม่เห็น session ของ CEO/desktop | ใช้ `scripts/token-report.py` (อ่าน DB ทั้งหมด) |
| `max_tokens` **ไม่ได้ส่งไป API** — ตัด string ปลายทางเท่านั้น | output ยาวจริงกว่าที่ขอ (กินโควตา) | ยังไม่ได้แก้ — ต้องเพิ่มการจำกัดฝั่ง prompt/agent |
| error แบบ plain text ไม่มี `retryAfterMs` | ล็อก 1 ชม. แทนเวลาจริง (~17.7 ชม.) | ตั้ง `SOLOCORP_LLM_LOCK_DEFAULT_S` หรือใช้ `--format json` |
| `opencode.db` โต 1.9 GB | query ช้าลงเรื่อย ๆ | ยังไม่มี housekeeping (งานแยก) |
| free tier ~300 request/วัน | งาน D3 (28 calls) พังถ้าวันนั้นใช้ไปเยอะ | เพดาน + lock ทำให้รู้ตัวก่อน ไม่ใช่หลัง |

---

## 7. หลักฐาน

| ไฟล์ | อะไร |
|:--|:--|
| `bus/evidence/2026-10-25/token-accounting/request-logs-summary.json` | สรุป 488 records (มี sha256 ของ export) |
| `bus/evidence/2026-10-25/token-accounting/smoke.log` | `think()` จริง: call แรก 0.98s / call ที่สอง 0.001s (0 LLM attempt) |
| `bus/evidence/2026-10-25/token-accounting/tests.log` | 82 passed (4 ไฟล์เทสต์ที่เกี่ยวข้อง) |
| `bus/evidence/2026-10-25/token-accounting/token-report.log` | รายงานจริงระหว่างโควตาล็อก |
| `tests/test_token_ledger.py` (42) · `tests/test_llm_provider_cmd.py` (28) | เทสต์ไม่ใช้ LLM |
