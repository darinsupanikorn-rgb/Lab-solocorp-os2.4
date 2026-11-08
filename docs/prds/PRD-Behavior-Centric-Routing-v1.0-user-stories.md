# User Stories — Behavior-Centric Routing

> **Feature:** Behavior-Centric Routing — Tier 0 Behavior Classifier
> **PRD:** `PRD-Behavior-Centric-Routing-v1.0.md`
> **Owner:** Product (โปรดัค)

---

## User Story 1: Behavior Classification (Happy Path)

**As a** Department Head (e.g., Engineering — ช่างฟูล)
**I want** requests ที่เกี่ยวกับ "implement" หรือ "เขียนโค้ด" ถูกส่งมาที่ Engineering โดยตรง
**So that** ผมไม่ต้องเสียเวลาส่งต่อ request ที่ department อื่นได้รับผิด

**Acceptance Criteria:**

```
Scenario: Request ถูก classify เป็น CODE_IMPLEMENTATION ด้วย confidence ≥ 90%
  Given มี request text: "implement login page with OAuth"
  When behavior classifier ทำงาน
  Then classification result มี CODE_IMPLEMENTATION เป็น winner
  And confidence score ≥ 0.90
  And request ถูก route ไป Engineering โดยตรง
  And metadata แนบ behavior_code = "CODE_IMPLEMENTATION" และ confidence score

Scenario: Request ภาษาไทยถูก classify ถูกต้อง
  Given มี request text: "ช่วยเขียน API endpoint สำหรับสร้าง user"
  When behavior classifier ทำงาน
  Then classification result มี CODE_IMPLEMENTATION เป็น winner
  And confidence score ≥ 0.90
```

**Priority:** P0
**Story Points:** 5

---

## User Story 2: Low Confidence → CEO Review

**As a** CEO (หนุมาน)
**I want** request ที่ behavior classifier ไม่มั่นใจ (confidence < 90%) ถูกส่งมาให้ผม review
**So that** ผมตัดสินใจ routing ที่ถูกต้อง และ data นี้ใช้ improve classifier ได้

**Acceptance Criteria:**

```
Scenario: Confidence ต่ำกว่า threshold ส่งไป CEO review queue
  Given classifier ทำงานกับ request ที่ ambiguous
  When highest confidence score < 0.90
  Then request ถูกส่งไป CEO Review Queue
  And แสดง top-3 candidate behaviors พร้อม confidence score
  And CEO สามารถเลือก department ที่ถูกต้องได้
  And หลังจาก CEO เลือก → request ถูก route ไป department นั้น

Scenario: CEO selection ถูกบันทึกเป็น training data
  Given CEO เลือก department สำหรับ request ที่ low confidence
  When selection เสร็จสิ้น
  Then ข้อมูล request + CEO label ถูก insert ลง training_data ตาราง
  And behavior ถูกบันทึกตาม department ที่ CEO เลือก
```

**Priority:** P0
**Story Points:** 3

---

## User Story 3: Non-Destructive Fallback

**As an** Architect (พี่ทรงศักดิ์)
**I want** behavior classifier ที่เมื่อ fail หรือ error จะ fall through ไปยัง routing ระบบเดิม
**So that** การเพิ่ม behavior layer ไม่กระทบระบบ routing ที่ทำงานอยู่ในปัจจุบัน

**Acceptance Criteria:**

```
Scenario: Classifier error — fallback ไป Tier 1 (keyword)
  Given classifier เกิด error (timeout / exception / model not loaded)
  When routing ทำงาน
  Then request ถูกส่งต่อไปยัง Tier 1 keyword matching
  And log ถูกบันทึก: "behavior_classifier_error" พร้อม reason
  And monitoring alert ถูกส่งถ้า error rate > 5% ใน 5 นาที

Scenario: Disable behavior layer — routing ทำงานเหมือนเดิม
  Given behavior_classifier_enabled = false (toggle)
  When request เข้ามา
  Then routing ข้าม Tier 0 ไป Tier 1 เลย
  And ไม่มีผลกระทบต่อ performance หรือ availability
```

**Priority:** P0
**Story Points:** 2

---

## User Story 4: Monitoring & Accuracy Visibility

**As an** Orchestrator (พี่วุฒิ)
**I want** dashboard ที่แสดง routing accuracy, false positive rate, และ CEO review volume
**So that** ผมรู้ว่าระบบ behavior routing ทำงานดีแค่ไหน และควรปรับปรุงตรงไหน

**Acceptance Criteria:**

```
Scenario: Dashboard แสดง routing metrics แบบ real-time
  Given behavior routing ทำงานอยู่
  When ผมเปิด dashboard
  Then เห็น metrics: routing accuracy (%), total requests, false positive rate (%)
  And เห็น CEO review queue size + average review time
  And เห็น trend graph — 7-day routing accuracy

Scenario: Alert เมื่อ metrics ต่ำกว่า threshold
  Given routing accuracy < 85% ในช่วง 1 ชั่วโมง
  When monitoring ตรวจสอบ
  Then send alert ไปยัง Architect + Orchestrator
```

**Priority:** P1
**Story Points:** 3

---

## User Story 5: Training Data Feedback Loop

**As a** Product Manager (โปรดัค)
**I want** ทุก CEO reassignment และ department re-route ถูกบันทึกเป็น training data อัตโนมัติ
**So that** classifier accuracy improve ได้เรื่อยๆ โดยไม่ต้อง manual label

**Acceptance Criteria:**

```
Scenario: CEO reassignment → auto-labeled training data
  Given CEO เปลี่ยน department ของ request ใน review queue
  When การเปลี่ยนเสร็จสิ้น
  Then training_data table มี record ใหม่
  And record มี: text, behavior (mapped จาก department), source="ceo_review", confidence="high"

Scenario: Department re-route → auto-labeled training data
  Given Department Head ส่งต่อ request ไป department อื่น
  When re-route เสร็จสิ้น
  Then training_data table มี record ใหม่
  And record มี: text, behavior, source="dept_reroute", confidence="medium"
```

**Priority:** P1
**Story Points:** 2

---

# Success Metrics — Behavior-Centric Routing

## North Star Metric

**Routing Accuracy** — % ของ request ที่ถูก route ไปยัง department ที่ถูกต้องในครั้งแรก

## Input Metrics (Leading Indicators)

| Metric | Definition | Current Baseline | Target | Measurement |
|:-------|:-----------|:----------------|:-------|:------------|
| **Behavior Classification Accuracy** | % ของ classification ที่ behavior winner ตรงกับ department ที่ถูกต้อง | N/A (new system) | ≥ 90% | Hold-out test set evaluation |
| **False Positive Rate** | % ของ request ที่ถูก route ผิด department | ~20-30% (estimated) | < 5% | CEO/department reassign rate |
| **CEO Review Volume** | % ของ request ที่ต้องเข้า CEO review queue | 100% (ambiguous requests) | < 10% | Review queue count / total requests |
| **Precision per Behavior** | Per-class F1 score | N/A | ≥ 0.85 | Per-behavior evaluation |

## Output Metrics (Lagging Indicators)

| Metric | Definition | Current Baseline | Target | Measurement |
|:-------|:-----------|:----------------|:-------|:------------|
| **First-Route Accuracy** | % ของ request ที่ถึง department ถูกต้องโดยไม่ต้อง re-route | ~70-80% | ≥ 95% | Department reassign event tracking |
| **CEO Re-route Time Saved** | เวลาที่ CEO ประหยัดได้จากการไม่ต้อง re-route | Current time spent re-routing | 80% reduction | CEO time tracking |
| **Average Time-to-Correct-Department** | เวลาจาก request → department ถูกต้อง | Current baseline | < 5 min | Central Bus audit log |
| **Training Data Growth** | # of labeled training samples | 1,300 (seed) | 5,000+ in 3 months | training_data table count |

## Guardrail Metrics (ต้องไม่ต่ำกว่า)

| Metric | Threshold | Action if Breached |
|:-------|:----------|:-------------------|
| **Classification Latency P95** | < 100ms | Disable behavior layer → fallback to existing routing |
| **System Uptime** | 99.9% | Emergency rollback |
| **False Negative Rate** (missed urgent request) | < 1% | Adjust threshold or add override rules |

## OKR Mapping

| Objective | Key Result | Metric Target |
|:----------|:-----------|:--------------|
| **ลด friction ในการ routing request ใน SoloCorp OS** | KR1: First-route accuracy เพิ่มจาก 70-80% → 95%+ | ≥ 95% |
| | KR2: CEO review volume ลดลง < 10% ของ total requests | < 10% |
| | KR3: Training data โตเป็น 5,000+ samples ภายใน 3 เดือน | 5,000+ |

---

**Prepared by:** Product (โปรดัค)
**Date:** 2026-07-20
