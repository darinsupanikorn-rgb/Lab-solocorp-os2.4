# 🛡️ API Key Protection Guide

> SoloCorp OS — ป้องกัน API Key Leak ไปบน GitHub

## Overview

ระบบป้องกัน 3 ชั้น:
1. **`.gitignore`** — ป้องกันไม่ให้ track `.env` files
2. **Pre-commit Hook** — สแกนหา secrets ก่อน commit
3. **Code Review** — human verification (L3+)

---

## 🔒 Layer 1: `.gitignore`

ไฟล์ที่ถูก ignore:

```gitignore
.env
.env.local
.env.production
*.key
*.pem
secrets.json
```

✅ **อยู่ใน `.gitignore` แล้ว** — ไม่ต้องทำอะไร

---

## 🚨 Layer 2: Pre-commit Hook

### อยู่ที่ไหน
```
.git/hooks/pre-commit
```

### Pattern ที่ตรวจสอบ

| Pattern | Example |
|---------|---------|
| `ccsk-[a-f0-9]{64}` | Maxplus AI API Key |
| `sk-[A-Za-z0-9]{48,}` | OpenAI API Key |
| `MAXPLUS_API_KEY=ccsk-` | Hardcoded Maxplus |
| `OPENAI_API_KEY=sk-` | Hardcoded OpenAI |
| `AWS_SECRET_ACCESS_KEY=` | AWS Secret |
| `GITHUB_TOKEN=` | GitHub Token |
| `password\s*=\s*['\"][^'\"]{8,}` | Password in code |

### การทำงาน

```bash
# ✅ ไฟล์ปกติ — commit ผ่าน
git add normal_file.py
git commit -m "Update code"
# 🔍 Checking for API keys and secrets...
# ✅ No secrets detected

# ❌ ไฟล์มี API Key — commit ถูก block
git add file_with_key.py
git commit -m "Add feature"
# 🔍 Checking for API keys and secrets...
# ❌ BLOCKED: Found potential API key in file_with_key.py
# 🚨 COMMIT BLOCKED: API Key หรือ Secret ถูกตรวจพบ!
```

### Bypass Hook (ระวัง!)

```bash
# ถ้าแน่ใจว่าไม่ใช่ secret จริง (เช่น test data)
git commit --no-verify
```

⚠️ **ใช้ `--no-verify` เฉพาะเมื่อแน่ใจ 100%!**

### ⚠️ Hook นี้เห็นแค่ "ของใหม่" — ต้องมี Layer 2.5

hook ตรวจ `git diff --cached` → คีย์ที่ commit ไปแล้ว **มองไม่เห็นตลอดกาล**
(incident 2026-10-25: คีย์จริง 2 ค่าอยู่ในประวัติมาเป็นเดือน)

```bash
bash scripts/secret-history-scan.sh --current   # 0.2s — ใส่ CI ทุก PR
bash scripts/secret-history-scan.sh             # + ทั้งประวัติ ~1m45s (รันก่อน release)
```

exit 1 = เจอค่าจริง (ค่าปลอม/dev key ที่ประกาศไว้จะถูกรายงานเป็น ℹ️ ไม่ทำให้ fail)

---

## 📋 Layer 3: Code Review Checklist

สำหรับ L3+ decisions:

- [ ] ไม่มี hardcoded API keys
- [ ] ไม่มี credentials ใน code
- [ ] ใช้ `os.getenv()` สำหรับ sensitive data
- [ ] `.env` ถูก ignore แล้ว
- [ ] `.env.example` ใช้ placeholder เท่านั้น

---

## 🏢 Layer 4: Console-side (สโคป / อายุ / หมุน / งบ)

> เพิ่ม 2026-10-25 หลังตรวจ `workspace-audit.json` — 3 ชั้นแรกกัน "คีย์หลุดเข้า git"
> แต่ไม่กัน "คีย์มีสิทธิ์เกิน" และ "ไม่มีเพดานงบ" ซึ่งเจอของจริงในวันเดียวกัน

| ข้อ | กฎ | เหตุผลจาก incident |
|:--|:--|:--|
| สโคป | คีย์สำหรับ inference ต้องเป็น `inference-only` — **ห้าม `all`** | `all` สั่งงาน workspace ได้ (สร้าง/revoke คีย์, เปลี่ยนโมเดล, สร้าง policy) → คีย์รั่ว 1 ตัว = ยึด workspace |
| อายุ | ≤ 90 วัน + ปฏิทินหมุน | audit เจอคีย์ 3 ตัวหมดอายุวันเดียวกันหมด (2027-01-23) ไม่มีแผนหมุน |
| จำนวน | 1 งาน = 1 คีย์ · เก็บไม่เกิน 2 ตัวที่มีชีวิต | audit เจอ 4 คีย์ใน 2 ชม. (สร้าง 3 / revoke 1) ชื่อไม่มีระบบ |
| งบ | budget policy ต้องมี **เพดานจริง** (>0) และครอบคลุมบัญชีอัตโนมัติ | เจอ `limitDollars: 0` + `except-service-accounts` → คนถูกบล็อก ระบบไม่ถูกคุม (กลับด้าน) |
| โมเดล | เปิดเฉพาะที่ใช้ · โมเดลแพง ($30/$180 per M) ต้องมีเหตุผล | audit เจอเปิด claude-opus-5 / gpt-5.5-pro พร้อมกัน ~30 ตัว |
| ตรวจ | ดาวน์โหลด `workspace-audit.json` เดือนละครั้ง แล้วเทียบกับรายการคีย์ที่ควรมี | audit log ระบุ actor + field-level change ครบ → ตรวจได้จริง |

### Incident 2026-10-25 — คีย์จริงอยู่ในประวัติของ repo ที่เป็น public

สแกนทั้ง 497 commits ด้วย `scripts/secret-history-scan.sh` → เจอ **ค่าจริง 2 ค่า**:

| # | อะไร | ที่ไหน | commit | สถานะ |
|:--|:--|:--|:--|:--|
| a | `MAXPLUS_API_KEY` ตัวจริง (ค่าเดียวกับ `.env` root) ใช้เป็น "ตัวอย่าง" 4 จุด | `docs/API-KEY-PROTECTION.md` | `c33a09a` | แทนด้วย `ccsk-REPLACE_WITH_NEW_KEY` แล้ว · **ยังไม่ rotate** |
| b | API key hardcoded เป็น fallback ในโค้ด | `workers/llm_provider.py` | `d6ec613` (ลบที่ `30e373a`, 2026-07-12) | ไม่อยู่ใน HEAD · **ยังอยู่ในประวัติ** |

ทั้งสอง commit **อยู่บน `origin/main` ของ repo public** (`Dr-SoloDev/Lab-solocorp-os2.4`)

| | |
|:--|:--|
| ทำไม hook ไม่จับ | hook สแกนเฉพาะ `git diff --cached` (ของใหม่) — ทั้งสองค่าถูก commit ก่อน/ตอนติดตั้ง hook |
| ยังต้องทำ | **rotate ทั้งสองค่า** (Owner) — การลบในไฟล์ไม่ทำให้ค่าที่เคย public ใช้ไม่ได้ |
| ทางเลือกเพิ่ม | `git filter-repo` ลบ commit `c33a09a` + `d6ec613` แล้ว force-push — ต้อง Owner อนุมัติ (destructive) และ **ทำหลัง rotate เท่านั้น** |

#### วิธีสแกนซ้ำ (ทำได้เอง ไม่ต้องรอ incident ใหม่)

```bash
bash scripts/secret-history-scan.sh --current   # tracked files (0.2s) — ใส่ CI ได้
bash scripts/secret-history-scan.sh --history   # ทั้ง 497 commits (~1m45s)
bash scripts/secret-history-scan.sh --all       # + ไฟล์ที่ gitignore (ตรวจเครื่องตัวเอง)
```

สคริปต์แยก **ค่าปลอม** (ทดสอบ/dev key ที่ประกาศไว้) ออกจาก **ค่าจริง** → exit 1 เฉพาะค่าจริง
และพิมพ์แค่ 12 ตัวอักษรแรก · advisory pattern จับ ENV-assignment ที่มีค่ายาว
(เช่น `LINE_CHANNEL_ACCESS_TOKEN`) ซึ่ง pattern มาตรฐานไม่จับ

> บทเรียน: **เอกสารความปลอดภัยเองก็เป็นที่รั่วได้** — ตัวอย่างในเอกสารต้องเป็นค่า fake
> ที่ผ่าน hook pattern หรือ placeholder ที่ไม่ใช่ hex จริง

---

## 🔧 How to Use API Keys Safely

### ✅ Correct Way

**1. Store in `.env`:**
```bash
MAXPLUS_API_KEY=ccsk-REPLACE_WITH_NEW_KEY
```

**2. Load in code:**
```python
import os

API_KEY = os.getenv("MAXPLUS_API_KEY", "")
if not API_KEY:
    raise ValueError("MAXPLUS_API_KEY not found in environment")
```

**3. Use `.env.example` as template:**
```bash
MAXPLUS_API_KEY=your-api-key-here
```

### ❌ Wrong Way

```python
# ❌ Hardcoded API key
API_KEY = "ccsk-REPLACE_WITH_NEW_KEY"

# ❌ Commented API key (still dangerous!)
# API_KEY = "ccsk-REPLACE_WITH_NEW_KEY"

# ❌ Config file tracked by git
config.json:
{
  "api_key": "ccsk-REPLACE_WITH_NEW_KEY"
}
```

---

## 🚨 What If API Key Leaked?

### Immediate Actions

1. **Revoke the key immediately** — ที่ provider dashboard
2. **Generate new key** — และอัพเดท `.env`
3. **Force push history rewrite** — ลบ key ออกจาก git history:

```bash
# ⚠️ Dangerous — ต้องทำใน safe environment
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

4. **Notify team** — ให้ทุกคน pull ใหม่
5. **Monitor usage** — ดูว่ามี unauthorized usage ไหม

---

## 📊 Testing Protection

### Test Pre-commit Hook

```bash
# Test 1: ไฟล์ปกติ (ควรผ่าน)
echo "print('hello')" > test.py
git add test.py
git commit -m "Test normal file"
# ✅ Should pass

# Test 2: ไฟล์มี API key (ควรถูก block)
echo "API_KEY='ccsk-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'" > test.py
git add test.py
git commit -m "Test with key"
# ❌ Should be blocked

# Cleanup
rm test.py
git reset HEAD test.py
```

### Test .gitignore

```bash
# .env ไม่ควรปรากฏใน status
git status
# ไม่มี .env ใน list

# แม้ force add ก็ควรถูก hook block
git add -f .env
git commit -m "Try to commit .env"
# ❌ Should be blocked by pre-commit hook
```

---

## 🔍 Audit Checklist

### สำหรับ Team Lead / Security Officer

- [ ] ตรวจสอบ `.gitignore` มี `.env` patterns
- [ ] Pre-commit hook ติดตั้งและใช้งานได้
- [ ] `.env.example` ไม่มี real API keys
- [ ] Code ทั้งหมดใช้ `os.getenv()` ไม่ hardcode
- [ ] Documentation อัพเดทให้ทีมรู้
- [ ] ทุกคนใน team รู้วิธี rotate keys เมื่อจำเป็น

---

## 📚 References

- `.gitignore` — Line 6, 102
- `.git/hooks/pre-commit` — Active hook script
- `.env.example` — Safe template
- `workers/maxplus_llm_provider.py` — Example of safe env usage

---

## 🆘 Support

หากพบ API key leak หรือมีคำถาม:

1. **Immediate:** Contact @ceo-hanuman หรือ @security
2. **Non-urgent:** สร้าง issue ใน repo (ไม่ใส่ key จริง!)
3. **Documentation:** อัพเดท doc นี้ตามสถานการณ์จริง

---

**Last Updated:** 2026-07-27
**Owner:** CEO (หนุมาน) + CyberSec Team
**Status:** ✅ Active Protection
