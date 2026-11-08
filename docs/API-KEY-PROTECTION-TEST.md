# 🧪 API Key Protection — Team Testing Guide

> **Goal:** ให้ทุกคนใน SoloCorp OS ทดสอบว่า pre-commit hook ทำงานได้

---

## 👥 Who Should Test

- [ ] CEO (หนุมาน)
- [ ] COO (กิจ/Kit)
- [ ] All Department Heads (19 departments)
- [ ] All Specialist Agents
- [ ] Anyone who commits code

---

## 🚀 Testing Instructions

### Step 1: Pull Latest Code

```bash
cd ~/projects/Lab-solocorp-os2.4
git pull origin main
```

**Expected:**
- ✅ Pre-commit hook อัพเดทอัตโนมัติที่ `.git/hooks/pre-commit`

**Verify:**
```bash
ls -la .git/hooks/pre-commit
# Should show executable file with recent date
```

---

### Step 2: Test Normal File (Should PASS)

```bash
# Create normal file
echo "print('Hello SoloCorp')" > test_normal.py

# Try to commit
git add test_normal.py
git commit -m "Test: normal file"

# Expected output:
# 🔍 Checking for API keys and secrets...
# ✅ No secrets detected
# [branch xxx] Test: normal file
```

**✅ Success Criteria:** Commit passes without errors

---

### Step 3: Test File with API Key (Should BLOCK)

```bash
# Create file with fake API key
echo "API_KEY = 'ccsk-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'" > test_secret.py

# Try to commit
git add test_secret.py
git commit -m "Test: should be blocked"

# Expected output:
# 🔍 Checking for API keys and secrets...
# ❌ BLOCKED: Found potential API key in test_secret.py
# 🚨 COMMIT BLOCKED: API Key หรือ Secret ถูกตรวจพบ!
```

**✅ Success Criteria:** Commit is blocked with error message

---

### Step 4: Test Force Add .env (Should BLOCK)

```bash
# Try to force add .env
git add -f .env 2>/dev/null
git commit -m "Test: .env should be blocked"

# Expected output:
# 🔍 Checking for API keys and secrets...
# ❌ BLOCKED: Found potential API key in .env
# 🚨 COMMIT BLOCKED: API Key หรือ Secret ถูกตรวจพบ!
```

**✅ Success Criteria:** Even with `-f`, commit is blocked

---

### Step 5: Cleanup Test Files

```bash
# Remove test files
rm -f test_normal.py test_secret.py

# Reset any staged changes
git reset HEAD test_normal.py test_secret.py .env 2>/dev/null

# Verify clean state
git status
```

**✅ Success Criteria:** Working directory is clean

---

## 📊 Report Your Results

### Format

```markdown
## Test Report — [Your Name/Department]

**Date:** YYYY-MM-DD
**Branch:** main
**Commit Hash:** [latest commit]

| Test | Result | Notes |
|------|--------|-------|
| Normal file (PASS) | ✅ / ❌ | |
| File with API key (BLOCK) | ✅ / ❌ | |
| Force add .env (BLOCK) | ✅ / ❌ | |
| Cleanup | ✅ / ❌ | |

**Issues Found:** None / [describe]

**Tested By:** [Your Name]
```

### Where to Report

**Option 1: GitHub Issue**
```bash
gh issue create --title "Test Report: API Key Protection" --body "[paste report]"
```

**Option 2: Bus Evidence**
```bash
# Save report
cat > bus/evidence/$(date +%Y-%m-%d)/api-key-test-[yourname].md << 'EOF'
[paste report here]
EOF
```

**Option 3: Slack/Discord**
Post in `#security` or `#dev-team` channel

---

## ❓ Troubleshooting

### Hook ไม่ทำงาน

**Symptom:** Commit ผ่านแม้มี API key

**Fix:**
```bash
# Check if hook exists and is executable
ls -la .git/hooks/pre-commit

# If not executable:
chmod +x .git/hooks/pre-commit

# If missing, copy from template:
cp scripts/pre-commit-template.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

---

### Hook ทำงานช้าเกินไป

**Symptom:** Hook ใช้เวลานาน >5 วินาที

**Check:**
```bash
# Run hook manually with timing
time .git/hooks/pre-commit

# Expected: <2 seconds for normal commits
```

**Report:** If consistently slow, report to @ceo-hanuman

---

### False Positive (block ไฟล์ปกติ)

**Symptom:** Hook block ไฟล์ที่ไม่มี secret

**Example:**
```python
# This might trigger false positive:
user_password_field = "sk-user-selected-name"  # Not a real API key
```

**Workaround:**
```bash
# Option 1: Rewrite code to avoid pattern
user_password_field = "user-selected-name"

# Option 2: Use --no-verify (only if 100% sure)
git commit --no-verify

# Option 3: Report pattern to improve hook
```

---

### ไม่รู้ว่า API key อยู่ตรงไหน

**Symptom:** Hook block แต่ไม่เห็นว่า key อยู่ไหน

**Debug:**
```bash
# Show full diff to find the key
git diff --cached | grep -C 3 "ccsk-\|sk-\|API_KEY"
```

---

## 🎯 Success Metrics

ทีมถือว่าผ่านการทดสอบเมื่อ:

- [ ] **100% ของทีม** ทดสอบ 4 test cases แล้ว
- [ ] **90%+ pass rate** — ส่วนใหญ่ผ่าน
- [ ] **All issues reported** — ปัญหาที่เจอถูกรายงาน
- [ ] **Zero real keys leaked** — ไม่มี real API key ถูก commit

---

## 📅 Testing Schedule

### Phase 1: Department Heads (Day 1-2)
- CEO, COO, Architect, Engineering Head, Product Head
- **Deadline:** 2026-07-29

### Phase 2: All Specialists (Day 3-5)
- All 19 departments + specialist teams
- **Deadline:** 2026-07-31

### Phase 3: Sign-off (Day 6)
- CEO reviews all reports
- System goes live for production
- **Deadline:** 2026-08-01

---

## 🏆 Rewards

- **First to complete:** Recognition in team meeting
- **Find critical bug:** Bonus points + security badge
- **100% team completion:** Team lunch sponsored by Owner

---

## 📞 Contact

**Questions:** @ceo-hanuman or #security channel
**Emergency:** If you accidentally commit real API key, contact CEO immediately

---

**Prepared By:** CEO (หนุมาน)
**Date:** 2026-07-27
**Version:** 1.0
