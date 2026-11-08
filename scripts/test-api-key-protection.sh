#!/bin/bash
# SoloCorp OS — API Key Protection Team Test
# Quick start script for team members

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🧪 API Key Protection — Team Test Runner             ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║   SoloCorp OS Security Testing                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get tester name from argument or prompt
if [ -n "$1" ]; then
    TESTER_NAME="$1"
else
    echo -e "${YELLOW}👤 Enter your name (e.g., 'turbo' or 'changful'):${NC}"
    read -r TESTER_NAME
fi

if [ -z "$TESTER_NAME" ]; then
    echo -e "${RED}❌ Name required! Usage: $0 <your-name>${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Starting test for: $TESTER_NAME${NC}"
echo ""

# Test results
TEST_1="PENDING"
TEST_2="PENDING"
TEST_3="PENDING"
TEST_4="PENDING"

# Test 1: Normal file
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 1: Normal File (should PASS)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "print('Hello SoloCorp')" > test_normal_$TESTER_NAME.py
git add test_normal_$TESTER_NAME.py
if git commit -m "Test: normal file by $TESTER_NAME"; then
    echo -e "${GREEN}✅ Test 1 PASSED: Normal file allowed${NC}"
    TEST_1="PASS"
else
    echo -e "${RED}❌ Test 1 FAILED: Normal file blocked (should not happen)${NC}"
    TEST_1="FAIL"
fi
echo ""
sleep 2

# Test 2: File with API key
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 2: File with API Key (should BLOCK)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "API_KEY = 'ccsk-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'" > test_secret_$TESTER_NAME.py
git add test_secret_$TESTER_NAME.py
if git commit -m "Test: should be blocked by $TESTER_NAME" 2>&1; then
    echo -e "${RED}❌ Test 2 FAILED: API key NOT blocked (security issue!)${NC}"
    TEST_2="FAIL"
else
    echo -e "${GREEN}✅ Test 2 PASSED: API key blocked${NC}"
    TEST_2="PASS"
fi
echo ""
sleep 2

# Test 3: Force add .env
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 3: Force Add .env (should BLOCK)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
git add -f .env 2>/dev/null || true
if git commit -m "Test: .env by $TESTER_NAME" 2>&1; then
    echo -e "${RED}❌ Test 3 FAILED: .env NOT blocked (security issue!)${NC}"
    TEST_3="FAIL"
else
    echo -e "${GREEN}✅ Test 3 PASSED: .env blocked${NC}"
    TEST_3="PASS"
fi
echo ""
sleep 2

# Test 4: Cleanup
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 4: Cleanup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
rm -f test_normal_$TESTER_NAME.py test_secret_$TESTER_NAME.py
git reset HEAD test_normal_$TESTER_NAME.py test_secret_$TESTER_NAME.py .env 2>/dev/null || true
git reset --soft HEAD~1 2>/dev/null || true

if git status | grep -q "nothing to commit\|Untracked files"; then
    echo -e "${GREEN}✅ Test 4 PASSED: Cleanup successful${NC}"
    TEST_4="PASS"
else
    echo -e "${YELLOW}⚠️  Test 4 WARNING: Manual cleanup may be needed${NC}"
    TEST_4="WARNING"
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Tester: $TESTER_NAME"
echo "Date: $(date +%Y-%m-%d)"
echo ""
echo "Test 1 (Normal file):   $TEST_1"
echo "Test 2 (API key):       $TEST_2"
echo "Test 3 (Force .env):    $TEST_3"
echo "Test 4 (Cleanup):       $TEST_4"
echo ""

# Overall result
if [ "$TEST_1" = "PASS" ] && [ "$TEST_2" = "PASS" ] && [ "$TEST_3" = "PASS" ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅ ALL TESTS PASSED!                                  ║${NC}"
    echo -e "${GREEN}║   API Key Protection is working correctly               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    OVERALL="PASS"
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ❌ SOME TESTS FAILED!                                 ║${NC}"
    echo -e "${RED}║   Please report to @ceo-hanuman immediately               ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    OVERALL="FAIL"
fi
echo ""

# Generate report
REPORT_FILE="bus/evidence/$(date +%Y-%m-%d)/api-key-test-$TESTER_NAME.md"
mkdir -p "bus/evidence/$(date +%Y-%m-%d)"

cat > "$REPORT_FILE" << EOF
# API Key Protection — Test Report

**Tester:** $TESTER_NAME
**Date:** $(date +%Y-%m-%d)
**Time:** $(date +%H:%M:%S)
**Branch:** $(git branch --show-current)
**Commit:** $(git rev-parse --short HEAD)

---

## Test Results

| Test Case | Expected | Result | Status |
|-----------|----------|--------|--------|
| 1. Normal file commit | ✅ Pass | $TEST_1 | $([ "$TEST_1" = "PASS" ] && echo "✅" || echo "❌") |
| 2. File with API key | ❌ Block | $TEST_2 | $([ "$TEST_2" = "PASS" ] && echo "✅" || echo "❌") |
| 3. Force add .env | ❌ Block | $TEST_3 | $([ "$TEST_3" = "PASS" ] && echo "✅" || echo "❌") |
| 4. Cleanup | ✅ Clean | $TEST_4 | $([ "$TEST_4" = "PASS" ] && echo "✅" || echo "⚠️") |

---

## Overall Assessment

**Status:** $OVERALL

$([ "$OVERALL" = "PASS" ] && echo "✅ **PASS** — All tests passed, system working correctly" || echo "❌ **FAIL** — Issues found, requires attention")

---

## Environment

- OS: $(uname -s)
- Git version: $(git --version)
- Shell: $SHELL
- Hook: $(ls -la .git/hooks/pre-commit 2>/dev/null | awk '{print $1, $9}')

---

## Sign-off

**Tested by:** $TESTER_NAME
**Date:** $(date +%Y-%m-%d)
**Generated:** Automated via test script

EOF

echo -e "${GREEN}📝 Report saved: $REPORT_FILE${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review your report: cat $REPORT_FILE"
echo "2. Update dashboard: bus/API-KEY-TEST-DASHBOARD.md"
echo "3. Announce completion in #security channel"
echo ""
echo -e "${BLUE}Thank you for testing! 🛡️${NC}"
