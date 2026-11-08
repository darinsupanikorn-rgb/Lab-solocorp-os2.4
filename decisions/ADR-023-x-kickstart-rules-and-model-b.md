# ADR-023: X Video Kickstart Bonus — Rules Engine + โมเดล B (เวิร์กโฟลว์)

**วันที่:** 2026-10-20
**สถานะ:** Accepted ✅
**Owner:** CEO หนุมาน (L4)
**ที่มา:** Owner ส่งข้อมูลโปรแกรม X "Video Kickstart Bonus" + สั่ง *"ด้านบนจบเราจะมาเริ่มหาเครื่องมือกับสร้างทำโมเดล B"*
**ต่อยอด:** ADR-022 (Creator Kit) · ADR-020 (news daily) · ADR-019 (web v1)
**แหล่งอ้างอิง (ทางการ):**
- Terms (ผูกพัน): `legal.x.com/en/x-creator-kickstart-bonus-terms` (Effective 2026-10-15)
- Help Center: `help.x.com/en/using-x/video-kickstart-bonus`
- Creator Monetization Standards: `help.x.com/en/rules-and-policies/content-monetization-standards`
- Original Content Rewards: `help.x.com/en/using-x/original-content-rewards`

---

## บริบท

Owner เลือกช่องทาง **X** (มีบัญชีอยู่แล้ว) และเจอโปรแกรมที่ตรงกับหมุด 4 พอดี:
**X Video Kickstart Bonus** — invite-only pilot, จ่าย **$1,000–$5,000** + **Premium+ ฟรี 1 ปี**
เงื่อนไข: โพสต์ **15 คลิปแนวตั้ง 9:16 (≠3 นาที) บน 15 วันที่แตกต่างกัน** ภายใน ~30 วัน

> นี่คือ **ตัวเลขจริงของหมุด 4** — ไม่ใช่ยอดไลค์ แต่เป็นเงิน + การมีงาน 15 ชิ้น

---

## 🔴 ข้อค้นพบที่เปลี่ยนบทบาทของ SoloCorp ทั้งหมด

จาก **Terms §4(a)** (ผูกพัน เหนือ Help Page):

> *"The Qualifying Video must be **yours**. You must have created the video…"*
> *"**not mass-produced solely to manufacture qualifying posts**, **not posted solely through unauthorized automation**"*

จาก **Original Content Rewards** (เป็นทางรับเงินของโปรแกรมนี้):
> *"Content will be ineligible if: … **Was created or posted using automated means**"*

### → ข้อสรุป

| ทาง | ผล | เหตุผล |
|:--|:--:|:--|
| ให้ AI **ผลิตคลิป** | ❌ **ไม่นับ** | "must be yours" + "mass-produced" |
| **โพสต์อัตโนมัติ** | ❌ **เสี่ยง** | "unauthorized automation" + OCR "automated means" |
| ให้ AI **คิดไอเดีย/เขียนสคริปต์** | ✅ **ปลอดภัย** | สคริปต์คือคำแนะนำ ครีเอเตอร์ถ่ายเอง = ของเขา |
| **ครีเอเตอร์กด Publish เอง** | ✅ **ปลอดภัย** | ไม่ใช่ automated posting |
| **นับวัน/เตรียม/ตรวจ** | ✅ **ปลอดภัย** | ไม่ได้ผลิตคอนเทนต์ ไม่ได้โพสต์ |

> 🎯 **บทบาทที่ถูกต้องของ SoloCorp = ผู้เตรียม · ผู้ตรวจ · ผู้จัดการเวลา**
> ไม่ใช่ "ผู้ผลิต" และไม่ใช่ "ผู้กดโพสต์"
> → ตรงกับ vision §5.3 **เป๊ะ** (คิดไอเดีย + ออกแบบสคริปต์ + เวิร์กโฟลว์) และ North Star ข้อ 1 ("ช่วยงานที่ไม่ถนัดดีขึ้น")
> → และ Owner เลือก "draft + กดยืนยัน 1 คลิก" ก่อนหน้านี้ = **ตรงกับนโยบาย X พอดี**

---

## การตัดสินใจ

### 1. เงื่อนไขโปรแกรม → Rules Engine (`solocorp_skills/programs/x_kickstart.py`)
แปลง Terms เป็นโค้ดที่ตรวจได้จริง:
- `PROGRAM` — ตัวเลขทั้งหมด (15 คลิป / 15 วัน / <180 วิ / 9:16 / เก็บโพสต์ 30 วันหลังรอบ)
- `DISQUALIFIERS` — 10 ข้อที่ทำให้หลุดนับ พร้อมอ้างอิง Terms §
- `ELIGIBILITY_GATES` — 7 gates รายบุคคล (18+, Premium, Stripe, email, good standing, invite/enroll)
- `probe_video()` / `check_video()` — ตรวจไฟล์ด้วย ffprobe (9:16, <3 นาที)
- `clip_checklist_md()` — checklist ต่อคลิป พร้อมสถานะโควตา

### 2. Pacific Time — หัวใจที่สุดของ tracker
- ทุก deadline เป็น PT (Terms §2) — **ไทย = PT + 15 ชม.**
- `pt_day_for_local()` — แปลงเวลาไทยเป็นวัน PT
- **`safe_posting_window_th() = ("15:00", "23:59")`** — โพสต์หลัง 15:00 ไทย = วัน PT ตรงกับวันไทยเสมอ
  (โพสต์ตี 2-3 ทุ่มไทย → นับเป็น **เมื่อวาน** ตาม PT → กินวันของเมื่อวานไปเปล่าๆ)
- `PostingTracker` — นับวันเอง เพราะ **tracker ของ X เป็นแค่ข้อมูลบอกทาง** (Terms §2.c) และ Final Count อาจต่ำกว่าได้ (§2.b)

### 3. โมเดล B — `loop_runner/loops/creator_daily.py`
```
ทุกเช้า (หลัง 07:00 ไทย)
  → เช็ค tracker: วันนี้โพสต์แล้วหรือยัง
  → ยังไม่โพสต์ → LLM คิด 3 ไอเดีย (จาก 4 ท่อน + ข่าวในคลัง)
  → สร้างแพ็กเกจ 5 ไฟล์ + checklist ตาม Terms
  → ส่ง inbox ให้ครีเอเตอร์ → ครีเอเตอร์ถ่าย/โพสต์เอง → บันทึกวัน
```
- **ไม่โพสต์แทน** · **ไม่ผลิตคลิป** · ใช้ข่าวจาก `news_daily` ในคลัง (ไม่เรียกเว็บซ้ำ)
- ทนทาน: LLM ตอบ JSON ไม่ครบก็ซ่อม parse ได้ (`_parse_json_array`)

### 4. ปรับ provider ให้รองรับ prompt ยาว
`think()` เพิ่มพารามิเตอร์ `timeout` — prompt ไทยยาวต้องใช้ >60 วิ (ค่า default เดิม)

---

## ⚠️ ความเสี่ยงที่ต้องบอกตรงๆ

| ความเสี่ยง | ผลกระทบ | การรับมือ |
|:--|:--|:--|
| **ไม่ได้เชิญ = ไม่ได้เงิน** | ทั้งหมดล้ม | **ข้อ 0: เช็ค Creator Studio ก่อน** |
| **ต้อง Premium + Stripe + ID verification** | ไม่ผ่าน = ไม่ได้เงิน | อยู่ใน eligibility checklist |
| **AI ทำคลิป = ไม่นับ** | หมุด 4 ไม่พิสูจน์ | บทบาทเรา = ผู้ช่วย ไม่ใช่ผู้ผลิต |
| **X รีวิวซ้ำหลังจบรอบ** | ตกแม้ tracker ขึ้นว่าผ่าน | เก็บหลักฐานเอง (origin log + tracker เรา) |
| **พลาดแค่ 1 วันจาก 15** | ตกทั้งรอบ | tracker เตือนทุกเช้า + ช่วงเวลาไทยปลอดภัย |
| **โปรแกรมอาจปิดทุกเมื่อ** (Terms §2.a, §16) | ความคุ้มค่าหาย | อย่าลงทุนเกินจำเป็น |
| **โพสต์ต้องคงอยู่อีก 30 วันหลังรอบ** | ลบทีหลัง = หลุดนับ | checklist เตือน + วันที่ต้องเก็บ |

---

## ผลกระทบ

**✅ ดี**
- มี "ตัวเลขจริง" ของหมุด 4 แล้ว: $1,000–5,000 + Premium+ ฟรี 1 ปี + 15 คลิป
- ได้ **โครงทีมตาม vision §5.3 เป๊ะ** และตรงกับข้อจำกัดของ X
- ใช้ของเดิมหมด: facts (โปรไฟล์) · news_daily (ข่าว) · media_pipeline (9:16) · creator-kit (4 ท่อน) · llm_provider (คิดไอเดีย)
- เทสต์: `tests/test_x_kickstart.py` **31/31** · regression 26 failed → 26 failed

**🔄 ยังไม่ทำ**
- ขั้นตอน "บันทึกวัน" แบบคลิกใน UI (ตอนนี้เป็น API) — เจ้าของรายงานกลับ
- โพสต์เป็น draft อัตโนมัติ (stealth-browser) — **ยังไม่ทำเพราะเสี่ยง Terms §4(a)**
- ตรวจลายน้ำอัตโนมัติ (ยังต้องให้คนดู)
- ตั้ง Stripe/ID verification

---

## ข้อ 0 — ต้องทำก่อนทุกอย่าง

> **เช็คว่าได้เชิญไหม:** X (แอป/เว็บ) → เมนูซ้าย → **Creator Studio** → ดูว่า **Video Kickstart Bonus** โผล่ไหม
> (ต้องเป็นบัญชี X Premium / Premium+ จึงจะเห็น Creator Studio ครบ · ลิงก์ตรง: `x.com/i/jf/creators/studio`)
> ถ้าไม่เห็น = ยังไม่ได้เชิญรอบนี้ → รอบถัดไป
>
> **Period 1: 15 ต.ค. – 14 พ.ย. 2026 (PT) · enroll deadline 30 ต.ค. 23:59 PT**
> = 31 ต.ค. เวลา 12:49 ไทย (PT+15)
