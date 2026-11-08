# CMD-005 Follow-up — Fallback Test Results (2026-09-27, Owner-ordered)

## Test 1 — 4 models direct (short prompt `Reply with just: PING`)
| Model | Result |
|:------|:-------|
| opencode/space-bunny-free | ✅ PING |
| opencode/muse-spark-1.3-contributor-free | ✅ PING |
| opencode/longcat-2.5-preview-free | ✅ PING |
| opencode/mimo-v2.6-flash-free | ✅ PING |
**4/4 alive**

## Test 2 — think() fallback with dead model
- `think(model='opencode/x-preview-f-free')` → `FALLBACK-OK` ✅
- Dead model skipped, live model answered

## Test 3 — DailyBriefLoop.run() end-to-end (2026-09-27)
- `should_run: True` (overdue since 2026-08-26)
- Log: `LLM เปล่า (opencode/space-bunny-free attempt 1)` → fallback to next model → success
- Result: Thai morning report from CFO meetoo (Finance offline / Watch items / CEO proposals)
- FAIL_CHECK: PASS (no `ไม่พร้อม` in output)

## Findings (new, for Architect CMD-005)
1. **Bus 401**: `curl /health` → busd alive but `{"code":"UNAUTHORIZED","message":"Invalid or missing API key. Use X-API-Key header."}`. `daily_brief._fetch_facts()` sends `Authorization: Bearer <key>` which busd no longer accepts → facts fallback to offline. Report itself noted: "Bus ต่อไม่ได้ (401)".
2. **Space Bunny empty on long Thai prompt**: first attempt returned empty on daily_brief's long prompt (same symptom as old deepseek issue 2026-08-04). Fallback covered it, but Architect should assess prompt sizing / per-model max_tokens.

## Files changed (this session, uncommitted)
- workers/llm_provider.py (DEFAULT_MODEL + MODEL_FALLBACKS + DEAD_MODELS + think() chain)
- opencode.json (ceo-hanuman model → space-bunny-free)
- .opencode/agents/*.md 21 files (x-preview-f-free → space-bunny-free)
- profiles/*/config.yaml untouched (MaxPlus system, Architect to decide)
