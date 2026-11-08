# 🔄 Handoff — สนามแรก (Creator Kit) · 2026-10-21

> เขียนเมื่อ context ใกล้เต็ม · อ่านไฟล์นี้ก่อนเริ่ม session ใหม่
> ดูรายละเอียดเชิงลึก: `decisions/ADR-022` (Creator Kit) · `ADR-023` (X program) · `ADR-025` (gate+series) · `ADR-026` (cadence)

---

## ✅ เสร็จแล้ว (commit แล้วทั้งหมด)

| อะไร | ที่ไหน |
|:--|:--|
| **โพสต์แรกขึ้นจริง** | `x.com/AChaisirum/status/2112593940096709038` · 270 ตัว · ผ่าน gate 8/8 |
| Web capability (อ่านเว็บ JS + ค้นหา) | `solocorp_skills/web.py` · `tools/carbonyl/` · ADR-019 |
| ข่าวรายแผนกทุกเช้า | `loop_runner/loops/news_daily.py` · ADR-020 |
| Rules engine ของโปรแกรม X | `solocorp_skills/programs/x_kickstart.py` · ADR-023 |
| Publish gate (ตัวกรองข้อมูล + R1-R5) | `solocorp_skills/redact.py` · ADR-025 |
| ซีรีส 5 แบบ + หมุนตามวัน | `solocorp_skills/creator.py` (`SERIES`) |
| สัญญาจังหวะ (แก้ด้วยมือ) | `bus/media/creator/cadence.md` · `solocorp_skills/cadence.py` · ADR-026 |
| โมเดล B (เตรียมคลิปให้ครีเอเตอร์ทุกเช้า) | `loop_runner/loops/creator_daily.py` |
| เครื่องมือเตรียมโพสต์ X (CDP) | `scripts/x_launch.sh` `x_type.py` `x_compose.py` `x_draft.py` |
| ทำคลิป 9:16 + เสียงไทย + ซับ | `scripts/make_clip.py` (piper + ffmpeg/libass) |

**สถานะระบบ:** คิว `0/0/0` · health 🟢 · เทสต์ 794 ผ่าน (26 fail เดิม ไม่เกี่ยว) · commits push แล้ว

---

## ✅ A เสร็จ — ซับไทย (2026-10-21)

| ไฟล์ | ผล |
|:--|:--|
| `bus/media/creator/dr-solodev/clips/Loop_Engineering_FULL_2m20s_9x16_SUB.mp4` | 720x1280 · 140.1วิ · 35.2MB ✅ |
| `bus/media/creator/dr-solodev/clips/SoloCorp_OS_Full_Evolution_108s_SUB.mp4` | 720x1280 · 88.3วิ · 25.4MB ✅ |

เครื่องมือ: `scripts/burn_subs.py` (ใหม่) — ตัดหัว markdown ออกจาก SRT ก่อน (libass อ่านไม่ได้) · MarginV=60 → ซับลงล่างพอดี 9:16
วิธีทำซ้ำ: `transcribe.py --model small --lang th --srt` → `burn_subs.py IN.mp4 --srt x.srt --out OUT.mp4`
(clips ไม่ commit — gitignore `bus/media/creator/*/clips/`)

## 🎙 เครื่องมืออัดเสียงบนเครื่องนี้ (ตรวจแล้ว 2026-10-21)

| เครื่องมือ | ที่อยู่ | ใช้ทำอะไร |
|:--|:--|:--|
| `ffmpeg` | `~/.local/bin/ffmpeg` | บันทึกหน้าจอ/เสียงผ่าน X11 หรือ PulseAudio + ตัด/เบิร์นซับ |
| `arecord` | `/usr/bin/arecord` | อัดไมค์ตรงจาก ALSA (การ์ด CX20588 Analog) |
| `pactl` / `pavucontrol` | `/usr/bin/` | ดู/ปรับระดับเสียง + เลือกอุปกรณ์อัด (PulseAudio) |
| `gst-launch-1.0` | `/usr/bin/` | GStreamer pipeline (อัดจาก X11/ไมค์) |
| `simplescreenrecorder` | `/usr/bin/` | บันทึกหน้าจอ (มีอยู่แล้ว) |

**ไม่มี:** obs / audacity / kdenlive / shotcut → ใช้ ffmpeg แทน
**อุปกรณ์อัด:** `card 0: PCH [HDA Intel PCH], device 0: CX20588 Analog`

คำสั่งอัดเสียงไมค์ (ทางเลือกที่ไม่ต้องเปิด GUI):
```bash
arecord -f cd -d 30 -c 1 -t wav ref.wav          # 30 วิ mono 44.1k
ffmpeg -f x11grab -i :0 -f pulse -ac 1 ref.wav   # จับหน้าจอ + เสียงระบบ
```

## 🎞 คลังวัสดุ b-roll (ค้นพบ 2026-10-21) — เปลี่ยนทุกอย่าง

`~/Videos/วีดีโอ ประวัติ Solodev/` = **81 ไฟล์** (ชื่อบอกชัด: ภาพ AI-generated)
| กลุ่ม | จำนวน | ใช้ทำอะไร |
|:--|:--:|:--|
| 9:16 · 10 วิ | **20 ไม่ซ้ำ** | b-roll พร้อมใช้ (ไม่นับโบนัส — AI-made) |
| 16:9 · 10 วิ | 58 | แปลงเป็น 9:16 ได้ (crop/pad) |
| มีเสียงพูด? | หลายไฟล์ | ต้อง transcribe + ซับไทย |

→ **นี่คือ "คลังวัสดุ" ของสนามแรก**: ครีเอเตอร์อัดเสียงอย่างเดียว → ระบบเลือก b-roll + ใส่ซับ + ตัดต่อ → ได้คลิปทุกวัน **โดยไม่ต้องถ่ายวิดีโอเลย**
→ และเป็นคลิปที่ **เนื้อหาตรงกับโลกของ SoloCorp** (CEO, ฮอโลแกรม, ไซเบอร์พันก์, ฉากคำสั่ง) — ไม่ใช่ภาพทั่วไป

### ⚠️ ข้อสรุปเชิงกลยุทธ์ (สำคัญที่สุดของ session นี้)
```
โบนัส (15 คลิป) = ต้องเป็น "ของครีเอเคร็อร์เอง" (Terms §4(a))
  → ครีเอเตอร์ถ่ายเอง : มี 11 ตัว · ขาดอีก 4
  → AI-made 20 ตัว : ไม่นับ
  → ต้องถ่ายเพิ่ม 4 คลิป = ภาระ → ความสม่ำเสมอพัง → ตัวตนพังด้วย
  → Owner เองบอก: "ไม่เก่งถ่ายวิดีโอ" + "ไม่เอารางวัลก็เอา การสร้างตัวตน"
คำแนะนำ: เลิกฝืนโบนัส → เดินเส้นทาง B (เสียงจริง + b-roll) ให้ตัวตนแข็งก่อน
          โบนัสค่อยมาตอนมีคลิปที่ถ่ายเองครบ 15 และอยากได้
```

## ✅ เส้นทาง B พิสูจน์แล้ว (2026-10-21)

`bus/media/creator/dr-solodev/clips/PATHB_trial01.mp4` — 40.0วิ · 1080x1920 · 26.2MB
→ 4 ท่อน × b-roll จับคู่ตามความหมายชื่อไฟล์ + ซับไทย + เสียงจริง · **ครีเอเตอร์ไม่ได้ถ่ายอะไรเลย**

เครื่องมือ: `scripts/make_broll_clip.py` + `bus/media/creator/dr-solodev/beat_broll.json` (แก้คำค้น b-roll ได้)

**ทำซ้ำ:**
```bash
python scripts/make_broll_clip.py --script X.script.md --library <โฟลเดอร์ b-roll> \
    --plan bus/media/creator/dr-solodev/beat_broll.json --audio <เสียง> --out OUT.mp4
```

### ⚠️ ข้อที่เหลือของเส้นทาง B (ต้องทำต่อ)
1. **เสียงต้องตรงท่อน** — ตอนทดลองใช้เสียงเดิมคลิป Loop_Engineering (140 วิ) ตัดเหลือ 40 วิแรก
   → ของจริง: คุณอัดเสียงให้ตรงกับสคริปต์ (arecord พร้อม) หรือเราตัดเสียงตามช่วงเวลาในสคริปต์
2. **b-roll มีข้อความไทยเบิร์นอยู่แล้ว** (เช่น "ฉอยใจที่แกรงขั้นมาก") → ทับกับซับของเรา
   → ต้องเลือก b-roll ที่ไม่มีข้อความ หรือให้ AI เลือกเฉพาะฉากที่สะอาด
3. **ซับท่อน 2 ยาว 4 บรรทัด** → ควรแบ่งเป็น 2 บรรทัดย่อย/ท่อน

## 🎬 คลิปที่นับโบนัสได้ (อัปเดต 2026-10-21)

```
~/Videos (19 ไฟล์)  → ผ่านขนาด+เวลา 10 → ไม่ซ้ำจริง 8
+ ตัดคลิปยาว 447 วิ (screen recording) → 3 ท่อน
══════════════════════════════════════
รวม 11 คลิป (ต้องตรวจลายน้ำ/ซ้ำเชิงเนื้อหาด้วยตาอีกรอบ) · ขาดอีก 4

**คลิปพร้อมซับไทยแล้ว 5 ตัว** (ใน bus/media/creator/dr-solodev/clips/ — ไม่ commit):
| ไฟล์ | ขนาด |
|:--|:--|
| Loop_Engineering_FULL_2m20s_9x16_SUB.mp4 | 35.2MB |
| SoloCorp_OS_Full_Evolution_108s_SUB.mp4 | 25.4MB |
| ScreenRec_20261020_part1_SUB.mp4 | 35.9MB |
| ScreenRec_20261020_part2_SUB.mp4 | 36.9MB |
| ScreenRec_20261020_part3_SUB.mp4 | 38.3MB |

💡 เนื้อหาใน screen recording = คุณคุยกับ CEO หนุมานเรื่องงานจริง (ADR-021 / Model Health Check)
→ คือ "เรื่องราวของเรา" ในรูปวิดีโอพอดี
```

**เครื่องมือใหม่:** `scripts/split_clips.py` (ตัดคลิปยาวเป็นท่อน ≤179 วิ ตาม Terms §4(a))

## ✅ Voice Clone ใช้ได้จริง (2026-10-21) — OmniVoice บน CPU

**แก้ torchaudio ได้แล้ว** (ติดตั้งครั้งแรกล้มเพราะ 2 อย่างพร้อมกัน):
1. `torchaudio` จาก PyPI = CUDA build → ต้อง `--index-url https://download.pytorch.org/whl/cpu` + เวอร์ชันให้ตรงกับ torch
2. `LD_LIBRARY_PATH` ต้องชี้ไปที่ `torch/lib` (ไม่งั้นหา libc10.so ไม่เจอ)

```
/data/venvs/omnivoice    torch 2.11.0+cpu · torchaudio 2.11.0+cpu · omnivoice 0.2.1
โมเดล: ~/.cache/huggingface/hub/models--k2-fsa--OmniVoice (2.5GB, cache ครบ)
เครื่องมือ: scripts/voice_clone.py  (ref-audio 3-10 วิ + ref-text → เสียง 24kHz)
```

**ผลทดสอบ:** ref = 10 วิ จาก Loop_Engineering (ศัพท์เดียวกับเป้าหมาย) → ผลลัพธ์ 5.2 วิ
ตรวจด้วย whisper: *"สวัสดีครับ วันนี้ผมจะเล่าให้ฟังว่า SoloCorp OS ทำอะไรได้บ้าง"* → **ถูกต้องอ่านออก**

### ⚠️ ข้อจำกัดสำคัญ: RTF 165 บน CPU
```
5.2 วิ เสียเวลา 858 วิ  →  คลิป 40 วิ จะใช้ ~1.8 ชั่วโมง
```
→ **เปลี่ยนวิธี: คิดเสียงทั้งสัปดาห์ล่วงหน้าในตอนกลางคืน (batch)**
   คืนนี้คิด 7 คลิป ≈ 4 ชม. → เช้ามาตัด b-roll + ซับ + โพสต์ → ได้วันละ 1 แบบไม่ต้องรอ
→ ต้องมี worker ที่ทำงานตอนกลางคืน (cron) + คิว

## 🔄 กำลังทำ (ค้างไว้)

**ติดตั้ง OmniVoice (voice cloning) แบบ CPU** — ⚠️ **ติดปัญหา torchaudio**
```
/data/venvs/omnivoice   ← venv (torch CPU ✅ / omnivoice ❌)
โมเดล: ~/.cache/huggingface/hub/models--k2-fsa--OmniVoice (3.1GB, cache ครบ ✅)
log:   /tmp/opencode/omnivoice_install.log
สาเหตุ: OSError: Could not load this library: .../torchaudio/lib/_torchaudio.abi3.so
→ ต้องจับคู่เวอร์ชัน torch/torchaudio ให้ตรงกัน (ลอง torch==2.8.0 + torchaudio==2.8.0)
→ แล้วรันบน CPU: device_map="cpu", dtype=torch.float32/bfloat16
```
⚠️ **หมายเหตุ: background job ต้องใช้ `setsid` ไม่ใช่แค่ nohup** — tool ตัด process group ตอน timeout

**ข้อจำกัดของเครื่องนี้:** ไม่มี GPU · RAM 15GB (ว่าง ~9GB) · โมเดล 2.45GB → CPU ได้แต่ช้า

---

## 📋 สิ่งที่ค้างรอ Owner

### 1. ⚠️ เรื่องเสียงพูดเพี้ยน — วัดแล้ว เจอสาเหตุ
- โมเดล whisper `base` อ่านเพี้ยนหนัก แต่ `small` อ่านออกเกือบทุกประโยค
  → **เสียงไม่ได้เสียมาก** ปัญหาคือ **ออกเสียงคำอังกฤษเป็นเสียงไทย** ("prompt"→"พร้อม", "Claude Code"→"คลอด คล")
- **คลิปไม่มีซับไทย** → คนดูไม่เข้าใจ → ต้องใส่ซับ
- ✅ **แก้ได้เลยด้วยของที่มีอยู่**: `scripts/transcribe.py --model small --lang th --srt` → เบิร์นด้วย `scripts/make_clip.py`

### 2. 🎯 คลิปที่มีอยู่ — นับโบนัสได้กี่ตัว
ตรวจ `/home/drsolodev/Videos` (18 ไฟล์) ด้วย `scripts/audit_clips.py`:
```
ผ่านขนาด+เวลา (9:16, <180วิ) : 10
ไม่ซ้ำจริง (md5)            : 8      ← ขาดอีก 7
```
| ไฟล์ | สถานะ |
|:--|:--|
| `Loop_Engineering_FULL_2m20s_9x16.mp4` | ✅ ครีเอเตอร์ on camera, ไม่มีลายน้ำ, 140วิ |
| `SoloCorp_OS_Full_Evolution_108s.mp4` | ✅ ครีเอเตอร์ on camera, 88วิ |
| `master_2_20_horizontal.mp4` | ✅ 704x1248, 140วิ — เนื้อหา**ต่าง**จาก Loop_Engineering (เทียบเฟรมแล้ว) |
| `image_20261010_*.mp4` ×5 | ⚠️ 10.2วิ — ภาพอนิเมชัน → **ต้องตัดสินใจว่านับไหม** (AI-made?) |
| `Inside_the_Ultimate_Junk_Shop_POS_System.mp4` | ❌ มีลายน้ำ **"© Canmore Animation"** → ไม่นับ |

### 3. 🔀 ทางแยกเรื่อง voice cloning กับโบนัส (ต้องตัดสิน)
Terms §4(a): *"The Qualifying Video must be **yours**"* → **คลิป AI/เสียง clone = ไม่นับ**
| ทาง | นับโบนัส? | ใช้ทำอะไรได้ |
|:--|:--:|:--|
| ครีเอเตอร์ถ่าย+พูดเอง → เราใส่ซับ/ตัด/ตรวจ | ✅ | 15 คลิป (ต้องถ่ายเพิ่ม 7) |
| AI ทำคลิป + เสียง clone | ❌ | สร้างตัวตน/ทดลอง/คอนเทนต์อื่น (ต้อง label AI) |

**ข้อเสนอ:** ทำ **2 อย่างขนานกัน**
- **ทางโบนัส** = ใส่ซับไทยให้คลิปที่ถ่ายเอง (ใช้ของที่มี) → ได้ 8 คลิปทันที ขาดอีก 7
- **ทาง voice cloning** = ทำเป็น capability ของ SoloCorp ให้ลูกศิษย์ + ครีเอเตอร์ (ตามที่ Owner สั่ง "ใช้ SoloCorp OS เหมือนกัน CEO ทำหน้าที่")

---

## ▶️ ขั้นถัดไป (เลือก 1 อย่าง)

| # | ทำอะไร | ใช้เวลา |
|:--|:--|:--|
| **A** | เบิร์นซับไทยให้ `Loop_Engineering` + `SoloCorp_OS` (transcribe small → SRT → libass) | 15 นาที |
| **B** | ทดสอบ OmniVoice clone เสียงจริง (ต้อง ref audio 3-10 วิ + ข้อความ) | 30 นาที |
| **C** | ตัดสินใจเรื่อง `image_2026*` (ภาพอนิเมชัน) นับโบนัสไหม | 5 นาที |
| **D** | เขียน skill `voice-clone` + เอกสาร เหมือนของอื่น | 30 นาที |

**คำแนะนำ: A → B** (ทำของที่ได้ผลกับโบนัสก่อน แล้วค่อยเปิด capability ใหม่)

---

## ⚠️ บันทึกไว้เพื่อไม่ลืม
- X ของ Owner **ยังไม่มี Premium** → ลิมิต 280 ตัวอักษร (ต้องมี Premium อยู่ดีสำหรับโปรแกรม X Kickstart ด้วย)
- วันที่ 30 ต.ค. 23:59 PT = 31 ต.ค. 12:59 ไทย = **deadline enroll รอบแรก**
- โปรแกรม X บังคับ **Premium + Stripe + ID verification** (คนนอกสหรัฐฯ) + บัญชี active ≥3 เดือน
- `skills/REGISTRY.md` ต้องเพิ่ม skill ใหม่ทุกครั้งที่สร้าง
- auto-commit loop จะ commit/push ให้เองทุก ~30 นาที (ระวัง: commit message มักผิด)
