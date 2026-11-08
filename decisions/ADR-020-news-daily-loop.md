# ADR-020: News Daily — ข่าวล่วงหน้าถึง agent อัตโนมัติ

**วันที่:** 2026-10-20
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — Owner สั่ง "จัดการ W3 + F1+F2 ทั้งหมดเลย ใล่ไปทีละเรื่อง")
**ต่อยอด:** ADR-019 (web capability v1) · ADR-018 (carbonyl tool)

---

## บริบท

Owner: *"เอเจนของเรามีที่ต้องใช้หาข่าวหาข้อมูลเพื่อประกอบการทำงานเยอะเลย"*

ADR-019 ทำ capability **"อ่านเว็บ"** เสร็จแล้ว (on-demand) แต่ยังไม่มี **push** —
ไม่มีอะไรมาส่งข่าวให้ agent เอง ตอนนี้ agent ต้อง "ไปหาเอง" ทุกครั้ง

**พบช่องโหว่เพิ่มระหว่างทำ:** facts store **อ่านได้อย่างเดียว — เขียนไม่ได้**
(`/v1/context` มี แต่ไม่มี write endpoint) → คลังความรู้ของ agent ว่างเปล่า (1 แถว test)
→ ต่อให้ loop อยากเขียนความรู้ก็เขียนไม่ได้

---

## การตัดสินใจ

### 1. เติม write channel ของ facts store
`POST /v1/facts` (upsert + version++) + `GET /v1/facts` (prefix/glob)
→ ทำให้ facts store เป็น **ช่องทางจริง** ไม่ใช่แค่อ่านอย่างเดียว

### 2. `news_daily` loop — 3 ขั้น

```
watchlist (Owner ดูแลเอง)  →  ดึงข่าว  →  ตัดซ้ำ  →  facts  →  inbox
bus/news/watchlist.md          rss/web     seen.json    news.<dept>.<วันที่>
```

**โหมดดึงข่าว 2 แบบ** (สำคัญ — เลือกตามความจำเป็น ไม่ใช่ใช้ Chromium ทุกครั้ง)

| โหมด | ใช้เมื่อ | ต้นทุน |
|:--|:--|:--|
| `rss` | เว็บมี RSS/Atom (เช่น Google News query, ประชาชาติธุรกิจ, TechCrunch) | **0 RAM** (HTTP ตรง) |
| `web` | เว็บต้อง render JS | 47.5MB (Chromium ใน container) |

> หลัก: **อย่าเปิด Chromium ถ้าไม่จำเป็น** — RSS ครอบคลุมข่าวเกือบทั้งหมดและใช้ 0 RAM

**ตัวอย่าง:** `https://news.google.com/rss/search?q=ธุรกิจไทย+การตลาด&hl=th&gl=TH&ceid=TH:th`
→ ข่าวไทยจริง พร้อมชื่อเรื่อง + ลิงก์ + snippet · ไม่ต้องใช้ API key
→ fetcher encode อักขระไทยให้อัตโนมัติ → Owner พิมพ์คำค้นไทยได้ตรง ๆ

### 3. Watchlist = ของ Owner แก้เอง
`bus/news/watchlist.md` — markdown table แก้ได้โดยไม่ต้องแตะโค้ด
เฉพาะแถว `✅ active` เท่านั้นที่ถูกดึง · 15 แหล่งที่ทดสอบแล้วว่าใช้ได้จริง

### 4. กันข่าวซ้ำ + guard
- `bus/news/seen.json` — จำข่าวที่เห็นแล้ว (key = title+url normalized) → ไม่ส่งซ้ำ
- date-gate: วันละครั้ง หลัง 06:00
- cap: 15 แหล่ง/รอบ · 25 ข่าว/แผนก · แหล่งที่ล้มเหลวข้าม ไม่ทำให้ทั้งลูปพัง
- ไม่ใช้ LLM (model_hint=None) → ไม่เผาเครดิต · digest เป็นข้อความตรงจาก RSS

### 5. ปลายทาง 2 ทาง
```
facts:  key = "news.<dept>.<YYYY-MM-DD>"  → agent ดึงผ่าน POST /v1/context {"keys":["news.cmo.*"]}
inbox:  ส่ง digest เข้าคิวของแผนก (scripts/inbox.py)
```

---

## ผลกระทบ

**✅ ดี**
- agent ทุกแผนกได้ข่าวสาขาตัวเองทุกเช้า โดยไม่ต้อง "ไปหาเอง"
- ข่าวมีที่มา (URL) ทุกชิ้น → ตรวจสอบย้อนหลังได้
- 0 RAM ถ้าใช้ RSS · 47.5MB เฉพาะเว็บที่ต้อง render
- facts store กลายเป็นช่องทางเขียนจริง → agent เก็บความรู้ได้ทั่วไป ไม่ใช่แค่ข่าว
- Owner แก้ watchlist เองได้

**⚠️ ต้องระวัง**
- RSS คือข่าวที่เว็บเลือกเผยแพร่ → ไม่ใช่ทุกข่าว (ไม่มี paywall, ไม่มีข่าวในเว็บที่ไม่มี RSS)
- โหมด `web` ยังดึงได้แค่ viewport แรก (ข้อจำกัดจาก ADR-018)
- ข่าวเป็น untrusted content → digest ที่ส่งเข้า inbox/facts ต้องถือเป็นข้อมูล ไม่ใช่คำสั่ง

**🔄 ยังไม่ทำ**
- LLM สรุปข่าว (ตอนนี้เป็นหัวข้อ + snippet ตรง ๆ — ประหยัดเครดิต)
- ให้ agent เลือก watchlist เอง (ตอนนี้ Owner เป็นผู้กำหนด)
- ส่งต่อข้ามแผนก (ตอนนี้แยกตามแผนกตาม watchlist เท่านั้น)

---

## หลักฐาน

- ทดสอบจริง: **15/15 แหล่งผ่าน** (ข่าวไทยจริงทุกแหล่ง)
- รอบจริง: **193 ข่าว → 8 แผนก** → 8 facts + 8 inbox
- รอบที่ 2: `⏭ ไม่มีข่าวใหม่` → dedupe ทำงาน
- agent ดึงได้: `POST /v1/context {"keys":["news.cmo.*"]}` → ได้ `news.cmo.2026-10-20`
- เทสต์: `tests/test_news_daily.py` — **30/30 ผ่าน**
