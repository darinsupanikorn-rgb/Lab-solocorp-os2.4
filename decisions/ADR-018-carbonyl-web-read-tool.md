# ADR-018: Carbonyl Web-Read Tool — อ่านเว็บ JS-rendered โดยไม่มี display

**วันที่:** 2026-10-20
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4 — ตัดสินแล้วรายงาน Owner)
**ที่มา:** Owner สั่ง — *"ตอนนี้เรามีทรัพยากรจำกัด กับเครื่องนี้ที่ฉันใช้งานอยู่ เลยคิดว่าเอามาใช้งานเฉพาะกับเรา มันจะลดการกินทรัพยากรได้"*

---

## บริบท

SoloCorp มี 3 ทางในการอ่านเว็บ:

| ทาง | RAM | ต้องมี display | ได้ JS-rendered |
|:--|:--|:--:|:--:|
| `webfetch` (HTTP) | 0 | ไม่ | ❌ ได้แค่ source code |
| `stealth-browser-mcp` (Chrome+CDP) | ~1.4GB | **ต้อง** | ✅ |
| **carbonyl** (Chromium ในเทอร์มินัล) | **47.5MB** | **ไม่** | ✅ |

Owner ต้องการลดการกินทรัพยากร → ต้องการทางที่ render JS ได้ **โดยไม่ต้องมี display**

## ข้อมูลอ้างอิง: `fathyb/carbonyl`

- Chromium ที่ patch ให้วาดลงเทอร์มินัล — Rust core (3,221 LOC) + C++ bridge (598 LOC) + 17 Chromium patches
- License **BSD-3-Clause** (ใช้เชิงพาณิชย์ได้)
- Upstream **หยุดพัฒนาตั้งแต่ 2023-02-27** (ไม่ archived) · ชุมชน fork เองที่ `carboxyl-rs/carboxyl` (active, Rust-native)
- ข้อจำกัดที่พบ: ไม่เก็บ cookie, ไม่มี Basic Auth/click, ไม่ผ่าน anti-bot, เห็นแค่ viewport แรก, `--dump-dom` ไม่ทำงาน
- npm `latest` tag ชี้ไปที่ **nightly prerelease** (`0.0.2-next.bacf3db`) ไม่ใช่ release → ห้ามใช้ `npm i -g carbonyl`

## การสืบสวน (หลักฐานวัดจริงบนเครื่อง Owner)

| ตัวชี้วัด | ค่า | วิธีวัด |
|:--|:--|:--|
| RAM | **47.5 MB** | cgroup `memory.current` (ไม่ double-count shared) |
| CPU idle | **0.03%** | cgroup `cpu.stat` `usage_usec` delta 10 วิ |
| ต้องมี display | ไม่ | `DISPLAY=[]`, ไม่มี process Xorg/cinnamon ใน container |
| Chrome (เทียบ) | ~1.4GB + 396MB GUI stack | RSS-sum 2.8GB (มี shared นับซ้ำ) + Xorg+cinnamon |

**พิสูจน์คุณค่าเฉพาะ (JS-only):**
- HTTP ธรรมดา → ได้ `<script>` source ไม่ใช่เนื้อหา
- carbonyl → ได้ `ข้อความนี้ถูกสร้างด้วย JavaScript เท่านั้น` หลัง execute จริง ✅

**พิสูจน์ภาษาไทย:** `th.wikipedia.org/wiki/ประเทศไทย` → `ประเทศไทย`, `84 ภาษา`, `บทความ` ✅

**ข้อจำกัดที่วัดได้:** `thairath.co.th` — เนื้อหาอยู่นอก viewport แรก (h1-h3 มี 20 อันใน DOM แต่ไม่อยู่ในจอ) → เว็บลักษณะนี้ใช้ HTTP ธรรมดาดีกว่า

## การตัดสินใจ

### 1. ใช้ ไม่ฟอร์ก
- ไม่ฟอร์ก upstream (17 patches, 100GB disk, 1 ชม. build = แพงเกิน SoloCorp)
- ไม่ผูกกับ `carboxyl-rs` (เพิ่งเกิด ยังไม่นิ่ง)
- บริโภคเป็น **tool** ผ่าน Docker image (`fathyb/carbonyl` → `solocorp/carbonyl-reader`)

### 2. ไม่มี binary ใน repo
- commit เฉพาะ Dockerfile + entrypoint.sh + extract.py + web-read (เล็ก)
- binary 405MB อยู่ใน Docker image เท่านั้น

### 3. Ladder 3 ขั้น (ประหยัดทรัพยากรจริง)
```
ขั้น 1  webfetch (HTTP)         0 RAM   ← เริ่มตรงนี้เสมอ
ขั้น 2  web-read (carbonyl)   47.5 MB   ← เมื่อขั้น 1 ได้แค่ source code
ขั้น 3  stealth-browser       ~1.4 GB   ← เมื่อต้อง interact / anti-bot / login
```

### 4. ทำเป็น skill ให้ทุกแผนกใช้
`skills/@solocorp/engineering/web-read/` — L1 (read-only) · consumers: cmo, content-creator, sales, support

## ผลกระทบ

**✅ ดี**
- ลด RAM จาก ~1.4GB → 47.5MB (30x) สำหรับงานอ่านเว็บ
- ไม่ต้องมี display → deploy บน VPS/box ที่ไม่มี GUI ได้
- `docker run --rm` → ไม่เหลือ container ค้าง
- รองรับภาษาไทยเต็มรอบ (grapheme segmentation ถูกต้อง)

**⚠️ ต้องระวัง**
- เห็นแค่ viewport แรก — ต้องมี fallback เป็น HTTP
- ไม่ผ่าน anti-bot / ไม่เก็บ cookie → เว็บที่ต้อง login ต้องใช้ขั้น 3
- ต้องมี Docker (dependency ใหม่ของ SoloCorp)
- เว็บแย่ง CPU ตอนโหลด (~180% ของ 1 core) — แต่ idle = 0

**🔄 ที่ยังไม่ทำ (ตั้งใจ)**
- ไม่ต่อเข้า Central Bus เป็น tool ของ agent (รอถ้ามี agent ที่ต้องอ่านเว็บจริง)
- ไม่แทน `stealth-browser` — ต่างหน้าที่กัน

## ทางเลือกที่พิจารณาแล้วไม่เลือก

| ทางเลือก | เหตุผลที่ไม่เลือก |
|:--|:--|
| ฟอร์ก `fathyb/carbonyl` | 17 Chromium patches + 100GB + 1 ชม. build — เกินกำลัง |
| ผูกกับ `carboxyl-rs/carboxyl` | เพิ่งตั้ง 2026-03-28 ยังไม่นิ่ง 163 stars |
| `npm i -g carbonyl` | `latest` tag = nightly prerelease ที่พังกว่า release |
| ใช้ Chrome เหมือนเดิม | กิน 1.4GB + ต้องมี display — ขัดกับเหตุผลที่ทำ |
| ทำทั้งเว็บ scraper เอง | ต้องเขียน JS engine เอง = ซ้ำงาน 60 ปี |

## หลักฐาน

`bus/evidence/2026-10-20-carbonyl-web-read.json` · ทดสอบสด: `tools/carbonyl/README.md`
