# CMD-005 Follow-up — 4-Model Fallback Implementation (Owner direct order 2026-09-27)

## Order
Owner สั่งตรง: fallback 4 โมเดล Space Bunny -> Muse Spark -> Longcat -> Mimo, ลุย 2 ชั้นทันที

## Changes (2 layers)

### Layer A — workers/llm_provider.py
- DEFAULT_MODEL: muse-spark → space-bunny-free
- Added MODEL_FALLBACKS (4): space-bunny / muse-spark / longcat-2.5-preview / mimo-v2.6-flash
- Added DEAD_MODELS map: x-preview-f-free, stealth/ox-alpha, deepseek-v4-flash-free → full chain
- think(): outer loop over models, inner retry; skip immediately on "Model not found"; empty response → next model; log fallback success
- Docstring updated

### Layer B — defaults
- opencode.json agent.ceo-hanuman.model: x-preview-f-free → space-bunny-free
- .opencode/agents/*.md 21 files: x-preview-f-free → space-bunny-free (verified uniq -c = 21)
- profiles/*/config.yaml (13, custom:maxplus-codex stealth/ox-alpha) — NOT touched, left for Architect CMD-005-T2 decision (separate MaxPlus system)

## Tests (live, 2026-09-27)
1. think('Reply OK') default model → RESULT: OK ✅ (space-bunny alive)
2. think(model='opencode/x-preview-f-free' dead) → RESULT: FALLBACK-OK ✅ (fallback chain works)
3. py_compile OK, import OK

## Remaining
- CMD-005-T1/T2 analysis by Architect still due 2026-09-30 (root cause + scheduler + profiles audit)
- daily_brief next run should now succeed via fallback even if one model dies
