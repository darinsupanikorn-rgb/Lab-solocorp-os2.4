# CEO Briefing — Behavior-Centric Routing

**From:** Product (โปรดัค)
**To:** CEO (หนุมาน)
**Date:** 2026-07-20
**Status:** ✅ PRD Finalized — รอ Architect Schema + Engineering Implementation

---

## สรุป 30 วินาที

Behavior-Centric Routing = เพิ่ม **intent classifier** ก่อนระบบ routing เดิม → request ถึง department ถูกต้องมากขึ้น → CEO ไม่ต้องเสียเวลา re-route

## Key Decisions Implemented

| Decision | Product Proposed | CEO Approved | Status |
|:---------|:----------------|:-------------|:-------|
| Taxonomy Size | 21 behaviors | **26 behaviors** ✅ | Documented in PRD |
| Confidence Threshold | 85% | **≥ 90%** ✅ | Built into classifier spec |
| Migration Strategy | Add-on | **Add-on (non-destructive)** ✅ | Architected as Tier 0 |
| Implementation Priority | Classifier first | **Data Schema first** ✅ | Week 1 focus |

## Deliverables Completed

### 📄 1. PRD ฉบับสมบูรณ์
**File:** `docs/prds/PRD-Behavior-Centric-Routing-v1.0.md`
- Problem statement + Why Now
- Solution architecture (Tier 0 add-on approach)
- 26-behavior taxonomy mapping (→ 18 departments)
- Confidence threshold logic (≥ 90% route, < 90% CEO review)
- Data schema design (taxonomy, training data, classification result)
- Technical approach: Embedding + Linear Classifier (not LLM)
- Implementation plan: 4 phases over 4 weeks
- In scope / out of scope / risks / dependencies

### 📖 2. User Stories (5 stories)
**File:** `docs/prds/PRD-Behavior-Centric-Routing-v1.0-user-stories.md`

| # | User Story | Priority | Points |
|:-:|:-----------|:---------|:-------|
| US-1 | **Happy Path** — request ถูก classify → routing ตรง department | P0 | 5 |
| US-2 | **Low Confidence** → CEO review queue + auto-label training data | P0 | 3 |
| US-3 | **Non-Destructive Fallback** — classifier fail → Tier 1-3 เลย | P0 | 2 |
| US-4 | **Monitoring Dashboard** — routing accuracy visibility | P1 | 3 |
| US-5 | **Feedback Loop** — CEO reassign → auto training data | P1 | 2 |

### 📊 3. Success Metrics

**North Star:** Routing Accuracy — % ของ request ที่ถูก route ถูก department ในครั้งแรก

| Target | Current | Goal |
|:-------|:--------|:-----|
| First-Route Accuracy | ~70-80% | **≥ 95%** |
| False Positive Rate | ~20-30% | **< 5%** |
| CEO Review Volume | 100% (ambiguous) | **< 10%** |
| CEO Re-route Time | Current | **80% reduction** |

### 🔧 4. routing.yaml Updated
**File:** `profiles/06-product/routing.yaml` → v2.0
- เพิ่ม 3 behavior-centric routing tasks
- behavior-taxonomy, behavior-classifier-spec, routing-metrics

---

## Next Steps & Timeline

```
Week 1 [Jul 20-26]:   🏗️ Data Schema Foundation — Architect (พี่ทรงศักดิ์)
                        • Schema design & validation
                        • SQLite tables + migration
                        
Week 2 [Jul 27-Aug 2]: 📋 Taxonomy + Training Data — Product + QA
                        • Finalize 26 behavior definitions
                        • Create seed data (50 samples/behavior = 1,300 total)
                        • Validate with historical requests

Week 3 [Aug 3-9]:      🧠 Classifier Implementation — Engineering (ช่างฟูล)
                        • Embedding + classifier pipeline
                        • Confidence scoring + threshold gate
                        • CEO review queue

Week 4 [Aug 10-16]:    🧪 Integration + Testing — QA + Engineering
                        • Integration test + A/B test
                        • Monitoring dashboard setup
                        • UAT → Go Live
```

## Requests to CEO

1. **CEO Review Queue preference:** Dashboard in Central Bus หรือ Slack notification? → รอ decision
2. **Cold start strategy:** Open monitoring ก่อน 2-3 วัน (classify but don't route) → OK?
3. **A/B test split:** 50/50 behavior routing vs existing routing → OK?

---

**Next Action:** รอ Architect (พี่ทรงศักดิ์) สร้าง data schema draft → Product review → ส่ง Engineering

✅ **PRD Approved** — พร้อม implement ตาม CEO decisions ทั้งหมด
