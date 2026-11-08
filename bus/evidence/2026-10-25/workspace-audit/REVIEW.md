# 🔍 Workspace Audit Review — 2026-10-25

**แหล่ง:** `/data/Videos/workspace-audit.json` (Owner ให้มา 2026-10-25 13:45 local)
**sha256:** `8edc59ce2147795a4cd50fdc1c857cfef25d1e90f4644eb110e6415a43288ecf`
**ขอบเขต:** 13 records · ทั้งหมด actor = `achaisirum@gmail.com` · source = `console`
**ตรวจโดย:** CEO (หนุมาน) · ยังไม่มีใครเซ็นรับ

> ⚠️ ไฟล์นี้ไม่มี secret (มีแต่ key **id** ไม่มีค่าคีย์) — เก็บเป็นหลักฐานได้
> ผมย่อ id ในรายงานนี้ (`sk_3010…`) เพื่อไม่ให้ id กระจายเกินจำเป็น

---

## 1. ไทม์ไลน์ (เวลาไทย)

| เวลา | การกระทำ | ผล |
|:--|:--|:--|
| 11:12 | key `Piask252534` → **permissions: inference-only → all** | 🔴 ยกระดับสิทธิ์คีย์เดิมเป็นเต็ม |
| 11:13 | สร้าง key `solocorp` (all, หมดอายุ 2027-01-23) | — |
| 11:20 | เปลี่ยน avatar workspace | — |
| 11:22 | เปิด/ปิด `web_search` integration 4 ครั้งใน 15 วินาที | 🟡 ร่องรอยการกดซ้ำ (ไม่มีความหมายเชิงระบบ) |
| 11:30 | สร้าง policy `policy_a6b9…` — audience **except** svc acct `…AHRR` | 🔴 ยกเว้นบัญชีอัตโนมัติจากนโยบาย |
| 11:30 | สร้าง policy-rule `budget`: **limitDollars 0** / per=set / period=month / scope=combined | 🔴 เพดาน $0 = บล็อกโมเดลเสียเงินทั้งหมด |
| 11:36 | **revoke** key `solocorp` (อายุ 23 นาที) | 🟢 เก็บกวาดแล้ว |
| 11:36 | สร้าง key `SOLOCORPOS` (all, svc acct `…AHRR`, หมดอายุ 2027-01-23) | 🟡 ซ้ำกับตัวถัดไป |
| 13:03 | เปิดโมเดลเสียเงิน ~30+ ตัวใน provider OpenCode (claude/gpt/gemini/glm/opus-5…) | 🟡 เปิดของแพงโดยไม่มีเพดานจริง |
| 13:22 | สร้าง key `solocorp01` (all, svc acct `…AHRR`, หมดอายุ 2027-01-23) | 🟡 คีย์ที่ 3 ที่ยังมีชีวิต |

## 2. สถานะปัจจุบัน (อนุมานจาก audit)

**คีย์ที่มีชีวิต 3 ตัว — ทุกตัว `permissions: all`:**

| key (ย่อ) | svc account | หมดอายุ | หมายเหตุ |
|:--|:--|:--|:--|
| `key_01M2…` (`Piask252534`) | (ไม่ระบุใน audit) | ไม่มีข้อมูล | เดิม `inference-only` → ถูกยกเป็น `all` วันนี้ |
| `sk_6cdc…` (`SOLOCORPOS`) | `…AHRR` (ยกเว้นจาก policy) | 2027-01-23 | |
| `sk_3010…` (`solocorp01`) | `…AHRR` (ยกเว้นจาก policy) | 2027-01-23 | สร้างล่าสุด |

**นโยบาย:** budget **$0/เดือน** กับทุกคน **ยกเว้น** svc account `…AHRR`
→ บัญชีที่ถือคีย์ของเรา = **ไม่ถูกคุมงบเลย** · คน/CLI ปกติ = **ถูกบล็อกที่ $0**

## 3. Findings (เรียงตามความรุนแรง)

### 🔴 F0 — คีย์จริงหลุดอยู่ใน repo **public** — **2 ค่า** (เจอเพิ่มระหว่างตรวจ audit นี้)

**สแกนประวัติทั้ง 497 commits** (pattern: `ccsk-…`, `oc_sk_…`, `sk-…`, Telegram bot token,
`ghp_…`, `AKIA…`, private key) ด้วย `scripts/secret-history-scan.sh`:

| # | ค่า (ย่อ) | ที่อยู่ | commit | สถานะวันนี้ | ต้องทำ |
|:--|:--|:--|:--|:--|:--|
| F0-a | `ccsk-8fc78b9…` | `docs/API-KEY-PROTECTION.md` (4 จุด) | `c33a09a` | ยังเป็นค่าจริงใน `.env` root | **rotate** |
| F0-b | `sk-gDFLCDp1p…` | `workers/llm_provider.py` (hardcoded fallback) | `d6ec613` → ลบที่ `30e373a` (2026-07-12) | ไม่อยู่ในไฟล์แล้ว แต่ยังอยู่ในประวัติ | **rotate ถ้ายังใช้ได้** |

ทั้งสอง commit **อยู่บน `origin/main` ของ repo public** (`Dr-SoloDev/Lab-solocorp-os2.4`,
`"visibility": "public"` — ตรวจผ่าน GitHub API 2026-10-25)

| | |
|:--|:--|
| ทำไม hook ไม่จับ | hook สแกน `git diff --cached` เท่านั้น (ของใหม่) — ทั้งสองค่าอยู่ใน commit เก่า |
| แก้แล้วโดยผม | F0-a: แทนด้วย `ccsk-REPLACE_WITH_NEW_KEY` (5 จุด) · F0-b: ไม่อยู่ใน HEAD ตั้งแต่ `30e373a` |
| **ยังต้องมี Owner** | **rotate ทั้งสองค่า** — ลบในไฟล์ไม่ทำให้ค่าที่เคย public ใช้ไม่ได้ |
| ทางเลือก | `git filter-repo` ลบ `c33a09a` + `d6ec613` แล้ว force-push (destructive, ต้องอนุมัติ และทำ**หลัง** rotate) |

**สรุปการสแกน:** ค่าจริง 2 ค่า (ข้างบน) · ค่าปลอม 1 ค่า (`ccsk-1234…` ×807 commit — ของทดสอบ hook)
· **ไม่พบ** Telegram bot token / GitHub PAT / AWS key / private key ในประวัติเลย
→ แปลว่า `.env` และ `profiles/*/.env` ไม่เคยถูก commit (ดี)

> 🔁 รันซ้ำได้: `bash scripts/secret-history-scan.sh` (~1m45s) · `--current` (~0.2s)
> หลักฐาน: [`secret-scan.log`](secret-scan.log)

### 🔴 F0.5 — คีย์กระจาย 27 จุดในเครื่อง ไม่มีแหล่งเดียว

`--all` สแกนไฟล์ที่ gitignore พบ **ค่าจริง 27 จุด** ใน `.env` + `profiles/*/.env`:

| ของ | จำนวน | หมายเหตุ |
|:--|--:|:--|
| `TELEGRAM_BOT_TOKEN` (ค่าเดียวกับทุกไฟล์) | 13 ไฟล์ | rotate ต้องแก้ 13 ที่ · ค่าเดียวกันหมด = รั่วที่ไหนก็รั่วหมด |
| `MAXPLUS_API_KEY` **2 ค่าไม่เหมือนกัน** | root `.env` = `ccsk-8fc7…` (F0-a) · `profiles/01-ceo,02-cfo` = `ccsk-09c8…` · อีก 11 profiles = `sk-loQGEZ…` | rotate ต้องรู้ว่าคีย์ไหนใช้ที่ไหน — ตอนนี้ไม่มีทะเบียน |
| `LINE_CHANNEL_ACCESS_TOKEN` | 1 (11-sales) | 172 chars, ไม่อยู่ใน pattern มาตรฐาน → advisory จับได้ |

→ **ข้อเสนอ:** ย้ายเป็น `.env` เดียวที่ root + ให้ profile อ่านผ่าน `SOLOCORP_*` (หรือ vault)
และทำ `docs/ENV-INVENTORY.md` ว่า key ไหนใช้ที่ไหน (ยังไม่ทำ — ต้อง Owner เคาะก่อน)

### 🔴 F1 — `permissions: all` ทั้ง 3 คีย์
`all` ไม่ใช่แค่ inference: มันสั่งงาน workspace ได้ (สร้าง/revoke คีย์, เปลี่ยนโมเดล,
สร้าง policy) → คีย์รั่ว 1 ตัว = ยึด workspace ได้ทั้งก้อน ไม่ใช่แค่กินโควตา
และคีย์หนึ่ง (`Piask252534`) **เพิ่งถูกยกระดับจาก `inference-only` → `all` วันนี้** โดยไม่มีเหตุผลบันทึกไว้

### 🔴 F2 — เพดานงบ $0 แต่ยกเว้นบัญชีอัตโนมัติ = กลับด้านความปลอดภัย
- คน/CLI (subject = ผู้ใช้) → **$0/เดือน** → ทุกโมเดลเสียเงินถูกบล็อก
- svc account `…AHRR` (เจ้าของ `SOLOCORPOS` + `solocorp01`) → **ไม่ถูกคุมเลย**
ผลคือ "คนถูกห้าม ระบบไม่ถูกห้าม" — ตรงข้ามกับที่ควรเป็น (ระบบอัตโนมัติควรถูกคุมแน่นกว่า)

### 🟡 F3 — หลักฐานชี้ว่า 402 `Insufficient account funds` มาจาก policy นี้
policy สร้าง 11:30 local · การทดสอบ paid model ของเรา 402 เวลา ~13:15 local (หลัง policy 2 ชม.)
→ **สมมติฐาน:** gateway แปลง "เกิน budget $0" เป็นข้อความ `Insufficient account funds`
**ทดสอบได้ใน 30 วินาที:** ตั้ง `limitDollars` เป็น 5 แล้วยิง `deepseek-v4.1-flash` 1 ครั้ง
- ผ่าน → ไม่ต้องเติมเงินเลย (แก้แค่ policy)
- ยัง 402 → กระเป๋าเงินว่างจริง ต้องเติม

### 🟡 F4 — Dashboard ขัดกับ audit
Owner เห็น "No budget policy" บน console แต่ audit มี policy `budget` มาตั้งแต่ 11:30
→ อย่าเชื่อหน้าเดียว · ตรวจที่เมนู Policies โดยตรง (หรือ UI แสดงเฉพาะ policy บางชนิด)

### 🟡 F5 — คีย์ซ้ำ 3 ตัว สโคปเดียวกัน หมดอายุวันเดียวกัน ไม่มีแผนหมุน
สร้าง 4 คีย์ / revoke 1 ภายใน 2 ชั่วโมง (11:12–13:22) · ชื่อไม่มีระบบ (`Piask252534`, `solocorp`,
`SOLOCORPOS`, `solocorp01`) → ตรวจไม่รู้ว่าตัวไหนใช้ที่ไหน ใครควรถูก revoke

### 🟡 F6 — เปิดโมเดลแพงโดยไม่มีเพดานจริง
13:03 เปิด claude-opus-5 ($5/$25), gpt-5.5-pro ($30/$180), gemini-3.1-pro ฯลฯ
ถ้า F2 ถูกแก้ให้บัญชี `…AHRR` มีงบ แต่ไม่มีเพดานต่อโมเดล → พลาดครั้งเดียวราคาสูงกว่าวันนี้ 100×

### 🟢 F7 — สิ่งที่ดีอยู่แล้ว
audit ระบุ actor/resource/field-level change ครบ → ตรวจย้อนได้จริง (ดีมาก เก็บไว้)
· repo **ไม่มี key id ของ console หลุด** (grep 0 ไฟล์ — แต่ดู F0: ค่า MAXPLUS หลุด คนละเรื่องกัน)
· `profiles/*/.env` ไม่ถูก track (gitignored) · root `.env` ไม่ถูก track
· revoke คีย์ทดสอบทิ้งภายในวันเดียวกัน

> ⚠️ แก้คำพูดตัวเอง: ตอนแรกผมเขียนว่า "repo ไม่มี key หลุด" โดยดูแค่ key id ของ console
> — พอสแกน pattern ของ MAXPLUS (`ccsk-…`) จึงเจอ F0 · **grep ต้องเลือก pattern ให้ตรงกับของที่ห่วง**
> ไม่ใช่ grep สิ่งที่เราบังเอิญนึกออก

## 4. สิ่งที่ผมแนะนำ (Owner ทำใน console — ผมทำแทนไม่ได้)

| # | การกระทำ | ทำไม | เวลา |
|:--|:--|:--|:--:|
| **0** | **rotate คีย์ 2 ตัว**: (a) `MAXPLUS_API_KEY` ปัจจุบัน `ccsk-8fc7…` (b) `sk-gDFLCDp1p…` ถ้ายังใช้ได้ | ทั้งคู่อยู่ในประวัติของ repo **public** (F0-a `c33a09a`, F0-b `d6ec613`) | 5 นาที |
| 1 | `limitDollars` 0 → **5** (monthly, combined) | ปลด 402 ถ้า F3 จริง + คุมค่าใช้จ่ายจริง | 1 นาที |
| 2 | ตัดสินใจเรื่อง exemption ของ `…AHRR` | ตอนนี้เป็นช่องเดียวที่ไม่ถูกคุม — ถ้าจำเป็นต้องมี ให้ตั้ง budget แยกให้มัน ไม่ใช่ยกเว้นลอย ๆ | 2 นาที |
| 3 | `Piask252534` → กลับเป็น `inference-only` | คีย์เครื่องส่วนตัวไม่ควรมีสิทธิ์ admin | 30 วิ |
| 4 | revoke `SOLOCORPOS` **หรือ** `solocorp01` (เก็บ 1) | ลดจุดรั่วจาก 3 → 2 | 30 วิ |
| 5 | ปิดโมเดลที่ไม่มีทางใช้ (opus-5, gpt-5.5-pro, daybreak ฯลฯ) | กันค่าใช้จ่ายพลาดแบบไม่ตั้งใจ | 2 นาที |
| 6 | ตั้ง expiry 90 วัน + ปฏิทินหมุนคีย์ | ลดหน้าต่างถ้าคีย์หลุด | — |

> หลังข้อ 1–2 ผมทดสอบ 402 ซ้ำได้ทันที (ไม่ต้องรอ 14:31 เพราะ 402 เป็นคนละเรื่องกับ 429)

## 5. สิ่งที่ผมทำแล้ว / ทำต่อได้เอง

**ทำแล้วในรอบนี้**
- แดง flag F0: แทนค่า MAXPLUS ที่หลุดใน `docs/API-KEY-PROTECTION.md` ด้วย `ccsk-REPLACE_WITH_NEW_KEY` (5 จุด)
- เขียน `scripts/secret-history-scan.sh` — สแกน tracked files + ประวัติ + ไฟล์ที่ gitignore
  · แยก "ค่าปลอม" (KNOWN_FAKE) ออกจาก "ค่าจริง" → exit 1 เฉพาะค่าจริง · พิมพ์แค่ 12 ตัวแรก
  · โหมด `--current` (0.2s) / `--history` (1m45s) / `--all`
  · advisory pattern จับ ENV-assignment ที่มีค่ายาว (เคส LINE token ที่ pattern มาตรฐานไม่จับ)
- สแกนประวัติ 497 commits → **เจอค่าจริง 2 ค่า** (F0-a, F0-b) · ค่าปลอม 1 ค่า · ไม่พบ Telegram/GitHub/AWS
- พบ F0.5: ค่าจริง 27 จุดในเครื่อง (`TELEGRAM_BOT_TOKEN` ซ้ำ 13 ไฟล์, MAXPLUS 2 ค่าไม่เหมือนกัน)
- เพิ่ม "Layer 4 — Console-side" ใน `docs/API-KEY-PROTECTION.md` (สโคป/อายุ/จำนวน/งบ/โมเดล/ตรวจรายเดือน)
  + บันทึก incident 2026-10-25 ไว้ในเอกสารเดียวกัน
- เก็บหลักฐาน: `workspace-audit.json` (sha256 ต้นฉบับ) · `REVIEW.md` นี้ · `secret-scan.log`

**ทำต่อได้ (ไม่ต้องรอ Owner)**
- ผูก `scripts/secret-history-scan.sh --current` เข้า CI (0.2s — ถูกพอจะรันทุก PR)
- เพิ่ม check เตือนถ้า `OPENCODE_CONSOLE_TOKEN` เป็นคีย์ `all` (ต้องมี audit export ประกอบ)
- อัปเดต `brain/learnt.md`: "เอกสารความปลอดภัยเองก็เป็นที่รั่วได้" + "grep ต้องเลือก pattern ให้ตรงกับของที่ห่วง"

**ต้อง Owner เท่านั้น**
- rotate MAXPLUS key · ลดสิทธิ์คีย์ · ตั้ง budget > 0 · ตัดสินใจเรื่อง history rewrite
