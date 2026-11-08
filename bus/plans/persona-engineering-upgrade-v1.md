# Persona Engineering + Quality System + Tools Integration

**Source:** teammate-skill research (https://github.com/Dr-SoloDev/teammate-skill)
**Owner:** CEO หนุมาน
**Status:** PLANNING
**Created:** 2026-07-12

---

## Scope

ยกระดับ SOUL.md profiles จาก flat markdown → structured 5-Layer Persona + Quality Gate + Evolution system

---

## Work Packages

### WP1: 5-Layer Persona Template — `@design-kreet`
- ออกแบบ template ใหม่สำหรับ `profiles/NN-name/SOUL.md`
- เพิ่ม Layer 0-5 structure (Core Personality, Identity, Communication, Decision, Interpersonal, Boundaries)
- migrate SOUL.md 18 profiles ไปใช้ template ใหม่
- **Output:** SOUL.md ใหม่ 18 profiles + template example

### WP2: Quality Gate Validation — `@architect-songsak`
- สร้าง `scripts/validate-soul-profiles.py`
- 7 criteria: concreteness, examples ≥3, catchphrases ≥2, priority ranking, scope defined, no generic filler, tag→rule translation
- Fail = auto-report พร้อมบรรทัดที่ต้องแก้
- **Output:** validate script + CI-ready

### WP3: Smoke Test Pipeline — `@qa`
- port 3 test prompts จาก teammate-skill smoke_test.md
- Domain, Pushback, Out-of-Scope — รันอัตโนมัติหลัง `/deploy`
- **Output:** smoke test module + /deploy integration

### WP4: Evolution Brain System — `@architect-songsak`
- ใช้ pattern version_manager.py → brain/ versioning
- append data → merge โดยไม่ overwrite
- rollback brain files ได้
- **Output:** brain/version_manager.py + `/brain` update

### WP5: Data Collector Tools — `@content-creator-sek`
- review tools: slack_collector.py, github_collector.py, email_parser.py
- ดูว่าอันไหนใช้กับ SoloCorp workflows ได้บ้าง
- **Output:** recommendation report + adapted scripts

### WP6: Privacy Guard → Legal Vault — `@legal-tulya`
- port privacy_guard.py PII scanner
- integrate กับ compliance pipeline
- **Output:** PII scan module + legal_vault integration

### WP7: Compare Mode — `@orchestrator-wut`
- design compare mode สำหรับ Department Heads
- ใช้ช่วย routing / handoff decision
- **Output:** spec + prototype command

---

## Timeline

| WP | Department | Owner | Target |
|:---|:-----------|:------|:-------|
| WP1 | Design | @design-kreet | W1 |
| WP2 | Architect | @architect-songsak | W1-W2 |
| WP3 | QA | @qa | W2 |
| WP4 | Architect | @architect-songsak | W2-W3 |
| WP5 | Content Creator | @content-creator-sek | W3 |
| WP6 | Legal | @legal-tulya | W3 |
| WP7 | Orchestrator | @orchestrator-wut | W4 |

---

## Handoff Chain

```
CEO หนุมาน (Vision + Plan)
  └── Orchestrator พี่วุฒิ (Timeline + Coordination)
        ├── Design ครีเอท → WP1
        ├── Architect พี่ทรงศักดิ์ → WP2 + WP4
        ├── QA QA-ทีม → WP3
        ├── Content Creator เสก → WP5
        ├── Legal ตุลย์ → WP6
        └── Orchestrator พี่วุฒิ → WP7
```
