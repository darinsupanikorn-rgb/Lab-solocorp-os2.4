# PRD: Behavior-Centric Routing

**Status:** Approved by CEO ✅
**Owner:** Product (โปรดัค)
**Target Release:** SoloCorp OS v0.7
**Date:** 2026-07-20
**Version:** 1.0.0

---

## Executive Summary

ระบบ routing ปัจจุบันของ SoloCorp OS ใช้ **keyword matching (Tier 1)** + **TF-IDF semantic matching (Tier 2)** เพื่อส่ง request ไปยัง department ที่ถูกต้อง ปัญหาคือ:

1. **ภาษาไทยจับคู่ keyword ได้ไม่ดี** — keyword-based routing ออกแบบมาเพื่อภาษาอังกฤษ
2. **Semantic threshold ต่ำ (0.22)** — ทำให้ false positive สูง
3. **ไม่มี fallback ระดับ confidence** — ถ้าส่งผิด planner/CEO ต้องมานั่ง re-route เอง

**Behavior-Centric Routing** เพิ่ม **Tier 0 — Behavior Classifier** เข้าไปก่อน Tier 1 (keyword) โดย classifier จะวิเคราะห์ **เจตนา/พฤติกรรม (intent/behavior)** ของ request แล้วส่งไปยัง department ที่ถูกต้องด้วย confidence score

### Key Decisions (CEO Approved)

| Decision | Choice | Rationale |
|:---------|:-------|:----------|
| **Taxonomy Size** | 26 behaviors | Architect proposal — ครอบคลุมทุก department + sub-behaviors |
| **Confidence Threshold** | ≥ 90% → department, < 90% → CEO review | High precision first, CEO as safety net |
| **Migration Strategy** | Add-on (non-destructive) | Behavior layer ก่อน tier 1 keyword — ไม่กระทบ routing เดิม |
| **Implementation Priority** | Data Schema → Classifier | Foundation ก่อน ML |

---

## 1. Problem Statement

> เมื่อมี request เข้ามาที่ Central Bus ระบบ routing ปัจจุบันไม่สามารถ identify **เจตนาที่แท้จริง** ของผู้ส่งได้ — อาศัย keyword matching และ semantic similarity เป็นหลัก ส่งผลให้ request 20-30% ถูกส่งผิด department และต้องเสียเวลา re-route

### ปัญหาที่ user (Department Heads) เจอ:
- Request มาผิด department ต้องสละเวลาส่งต่อ
- Request ที่เป็นภาษาไทย ambiguous — routing ไม่แน่ใจว่า "แก้บั๊ก" ควรไป Engineering หรือ QA
- ไม่มี confidence indicator — department ไม่รู้ว่าระบบมั่นใจแค่ไหนที่ส่ง request นี้มา

### ปัญหาที่ CEO/Planner เจอ:
- ไม่มี visibility ว่า routing ผิดบ่อยแค่ไหน
- ต้องมานั่ง re-route request ที่ผิด department ด้วยตัวเอง
- ไม่มี data สำหรับปรับปรุง routing rules

---

## 2. Why Now

1. **SoloCorp OS กำลัง scale** — มี 18 departments แล้ว การ routing ผิดจะเพิ่มต้นทุนการทำงาน
2. **Thai language routing limitation** — ระบบปัจจุบัน (TF-IDF + keyword) ไม่ robust สำหรับภาษาไทย
3. **CEO time is expensive** — ทุกครั้งที่ CEO ต้อง re-route request เสียเวลาโดยใช่เหตุ
4. **Data schema is ready** — Central Bus v0.6 มี SQLite backend + RoutingEngine ที่ expandable ได้

---

## 3. User Segments

| Segment | ใคร | Benefit |
|:--------|:----|:--------|
| **Primary** | Department Heads (18 departments) | ได้ request ที่ตรง department ลดเวลา re-route |
| **Primary** | CEO / Orchestrator | ลด cognitive load ในการ re-route |
| **Secondary** | Senders (agents, users) | Request ถึง department ถูกต้องเร็วขึ้น |
| **Secondary** | Central Bus | Routing accuracy เพิ่มขึ้น ลลด waste |

---

## 4. Solution Overview

### 4.1 Architecture Change

```
Current:
  [Request] → Tier 1: Keyword Match → Tier 2: Semantic (TF-IDF) → Tier 3: CEO Fallback

New:
  [Request] → Tier 0: Behavior Classifier (NEW) → Tier 1: Keyword Match → Tier 2: Semantic (TF-IDF) → Tier 3: CEO Fallback

  Behavior Classifier Flow:
  [Request Text] → Behavior Classification Model → 26 behavior scores
    ├── Best score ≥ 90% → Route to mapped department
    └── Best score < 90% → CEO review queue (with top-3 candidate behaviors)
```

### 4.2 Add-on (Non-Destructive)

- Behavior layer **เพิ่มก่อน** Tier 1 keyword — ไม่ลบหรือแก้ routing logic เดิม
- ถ้า behavior classifier ไม่สามารถ classify ได้ (confidence < 90% หรือ error) → fall through ไป Tier 1-3 เหมือนเดิม
- **Rollback:** disable behavior layer → ระบบกลับไปใช้ routing เดิมทันที

### 4.3 26-Behavior Taxonomy

| # | Behavior Code | Behavior Name | Map to Department | ตัวอย่าง Request |
|:-:|:--------------|:--------------|:------------------|:-----------------|
| 1 | `VISION_STRATEGY` | Vision & Strategy | CEO | "ทิศทางบริษัทปีหน้าควรเป็นยังไง" |
| 2 | `CROSS_DEPT_ESCALATION` | Cross-dept Escalation | CEO | "ทีม Design กับ Engineering ตกลงกันไม่ได้" |
| 3 | `EXTERNAL_COMMS` | External Communication | CEO | "มีพาร์ทเนอร์ขอคุยกับผู้บริหาร" |
| 4 | `BUDGET_PLANNING` | Budget Planning | CFO | "ขอดูงบประมาณ Q4" |
| 5 | `FINANCIAL_REPORTING` | Financial Reporting | CFO | "ส่งรายงานการเงินประจำเดือน" |
| 6 | `INVESTMENT_ANALYSIS` | Investment & Cost Analysis | CFO | "วิเคราะห์ ROI feature นี้" |
| 7 | `MARKETING_CAMPAIGN` | Marketing Campaign | CMO | "แคมเปญเปิดตัวสินค้าใหม่" |
| 8 | `BRAND_POSITIONING` | Brand Positioning | CMO | "ทบทวน brand guideline" |
| 9 | `PIPELINE_COORDINATION` | Pipeline Coordination | Orchestrator | "ประสานงานข้ามแผนก 3 ทีม" |
| 10 | `WORKFLOW_AUTOMATION` | Workflow Automation | Orchestrator | "ตั้งค่า pipeline auto-approve" |
| 11 | `SYSTEM_ARCHITECTURE` | System Architecture | Architect | "ออกแบบระบบใหม่รองรับ user 10x" |
| 12 | `ROUTING_CONFIG` | Routing Configuration | Architect | "เพิ่ม route ใหม่จาก Marketing ไป Sales" |
| 13 | `PRODUCT_FEATURE` | Product Feature Request | Product | "ขอ feature export PDF" |
| 14 | `ROADMAP_PRIORITY` | Roadmap & Priority | Product | " roadmap Q3 priority อะไรบ้าง" |
| 15 | `CODE_IMPLEMENTATION` | Code Implementation | Engineering | "implement login page" |
| 16 | `DEPLOYMENT_RELEASE` | Deployment & Release | Engineering | "deploy version 2.1 ขึ้น production" |
| 17 | `UX_RESEARCH_DESIGN` | UX Research & Design | Design | "วิจัย user กลุ่มเป้าหมายใหม่" |
| 18 | `UI_COMPONENT` | UI Component | UI Designer | "ออกแบบ button component ใหม่" |
| 19 | `QUALITY_TESTING` | Quality Testing | QA | "ทดสอบ regression ก่อน release" |
| 20 | `SALES_DEAL` | Sales Deal | Sales | " closing deal ลูกค้า enterprise" |
| 21 | `CUSTOMER_SUPPORT` | Customer Support | Support | "ลูกค้าแจ้งปัญหาล็อกอินไม่ได้" |
| 22 | `LEGAL_COMPLIANCE` | Legal & Compliance | Legal | "ตรวจสอบสัญญากับ vendor" |
| 23 | `BLOCKCHAIN_DEFI` | Blockchain & DeFi | Web3 | "ออกแบบ smart contract token" |
| 24 | `CONTENT_CREATION` | Content Creation | Content Creator | "ทำวิดีโอโปรโมท feature ใหม่" |
| 25 | `NETWORK_INFRA` | Network Infrastructure | Network Engineer | "ตั้งค่า CDN สำหรับ static assets" |
| 26 | `SECURITY_INCIDENT` | Security Incident | Cyber Security | "มี suspicious activity ในระบบ" |

> **Note:** Psychology (`BEHAVIOR_INSIGHT`) ไม่ได้เป็น standalone behavior ใน 26 นี้ — พฤติกรรมด้าน Psychology จะถูก routed ผ่าน `VISION_STRATEGY` (ระดับองค์กร), `UX_RESEARCH_DESIGN` (ผู้ใช้), หรือ `CROSS_DEPT_ESCALATION` (ทีม) ขึ้นอยู่กับบริบท ถ้าข้อมูลการใช้งานชี้ว่าควรมี behavior แยก สามารถเพิ่มเป็น #27 ได้ในการ iteration ถัดไป

### 4.4 Confidence Threshold Logic

```
Classifier Output: [behavior_1: 0.92, behavior_2: 0.04, behavior_3: 0.02, ...]

ถ้า highest_score ≥ 0.90:
  → Route to mapped department ทันที
  → แนบ behavior_code + confidence score ไปกับ message metadata

ถ้า highest_score < 0.90:
  → ส่งไป CEO Review Queue
  → แนบ top-3 candidate behaviors + scores
  → CEO เลือก department ที่ถูกต้อง (ใช้เป็น training data ด้วย)

ถ้า classifier error/timeout:
  → Fall through ไป Tier 1-3 (existing routing)
  → Log error สำหรับ monitoring
```

### 4.5 Data Schema (Foundation — Priority #1)

ก่อนสร้าง classifier ต้องมี data schema สำหรับ:

```json
{
  "behavior_taxonomy": {
    "version": "1.0.0",
    "behaviors": [
      {
        "code": "CODE_IMPLEMENTATION",
        "name": "Code Implementation",
        "description": "Request for coding, implementation, or development work",
        "department": "engineering",
        "keywords": ["implement", "เขียนโค้ด", "develop", "build feature"],
        "examples": ["implement login page", "เขียน API endpoint ใหม่"],
        "synonyms": ["development", "coding", "programming"]
      }
    ]
  },
  "training_data": {
    "version": "1.0.0",
    "samples": [
      {
        "id": "sample-0001",
        "text": "implement login page with OAuth",
        "behavior": "CODE_IMPLEMENTATION",
        "source": "historical_routing",
        "confidence": "exact",
        "timestamp": "2026-07-20T00:00:00Z"
      }
    ]
  },
  "classification_result": {
    "message_id": "msg-xxxx",
    "behavior_scores": {
      "CODE_IMPLEMENTATION": 0.92,
      "DEPLOYMENT_RELEASE": 0.04,
      "QUALITY_TESTING": 0.02
    },
    "winner": "CODE_IMPLEMENTATION",
    "confidence": 0.92,
    "threshold_met": true,
    "routed_to": "engineering",
    "fallback_tier_used": false
  }
}
```

---

## 5. Requirements

### 5.1 Must Have (P0) — Data Schema Foundation

| # | Requirement | Acceptance Criteria |
|:-:|:------------|:-------------------|
| R1 | **Behavior Taxonomy Schema** — JSON schema สำหรับ 26 behaviors | Schema validated: ทุก behavior มี code, name, description, department, keywords |
| R2 | **Training Data Schema** — JSON schema สำหรับ labeled training samples | Schema validated: รองรับ text, behavior label, source, confidence level |
| R3 | **Classification Result Schema** — JSON schema สำหรับ output ของ classifier | Schema validated: behavior_scores map, winner, confidence, threshold_met |
| R4 | **Behavior ↔ Department Mapping** — 1-to-1 mapping table | 26 behaviors mapped to 18 departments (บาง department มี >1 behavior) |
| R5 | **Central Bus Storage** — store taxonomy + training data ใน SQLite | Tables: `behavior_taxonomy`, `training_data`, `classification_log` |

### 5.2 Must Have (P0) — Classifier

| # | Requirement | Acceptance Criteria |
|:-:|:------------|:-------------------|
| R6 | **Behavior Classification Pipeline** — classify request text เป็น 1 ใน 26 behaviors | Input: string → Output: dict of behavior→score |
| R7 | **Confidence Scoring** — normalized score 0.0-1.0 | Sum of all scores = 1.0 |
| R8 | **Threshold Gate** — ≥ 0.90 route, < 0.90 CEO review | Configurable threshold (env var) |
| R9 | **Fallback Logic** — tier fallthrough เมื่อ confidence < threshold | Graceful degradation → Tier 1-3 |
| R10 | **CEO Review Queue** — Interface สำหรับ CEO ดูและ reassign | Top-3 candidates shown per item |

### 5.3 Should Have (P1)

| # | Requirement | Acceptance Criteria |
|:-:|:------------|:-------------------|
| R11 | **Feedback Loop** — CEO reassignment ถูกบันทึกเป็น training data | ทุก reassignment → insert ลง training_data table |
| R12 | **Monitoring Dashboard** — routing accuracy, false positive rate, CEO review volume | Grafana / dashboard metric |
| R13 | **A/B Testing Mode** — เปรียบเทียบ accuracy behavior routing vs existing routing | Random 50% traffic分流 |

### 5.4 Nice to Have (P2)

| # | Requirement | Acceptance Criteria |
|:-:|:------------|:-------------------|
| R14 | **Multi-language Support** — classify request ทั้งไทย/อังกฤษ/ผสม | Accuracy ≥85% ในทุกภาษา |
| R15 | **Auto-retrain Pipeline** — retrain model เมื่อ training data เพิ่มถึง threshold | Trigger เมื่อ +100 samples |
| R16 | **Explainability** — แสดงเหตุผลที่ classifier เลือก behavior นี้ | Top-3 keywords ที่มีน้ำหนักมากที่สุด |

---

## 6. Technical Approach

### 6.1 Model Approach: Embedding + Linear Classifier

**เลือกใช้:** Embedding + Linear Classifier (ไม่ใช่ LLM API)

**Rationale:**
1. **Latency:** embedding classifier ใช้เวลา < 50ms ต่อ request (vs LLM 1-5s)
2. **Cost:** embedding ถูกกว่า LLM inference 100-1000x
3. **Deterministic:** ให้ผลลัพธ์เหมือนเดิมทุกครั้ง (vs LLM ที่ variance สูง)
4. **Iterate ได้:** เพิ่ม training data → retrain ใน 2 นาที
5. **Offline ได้:** ไม่ต้องต่อ internet — ทำงานใน SoloCorp environment ได้

**Approach:**
- Use `sentence-transformers` (หรือ `fasttext` สำหรับ multilingual) สำหรับ text embedding
- Train linear classifier (Logistic Regression / SVM) บน embedding vectors
- Thai support: use multilingual embedding model (e.g., `distiluse-base-multilingual-cased`)

### 6.2 Training Data Strategy

**Phase 1 — Seed Data (initial launch):**
- 50 samples per behavior = 1,300 labeled samples
- Source: historical routing logs + human-labeled
- สร้าง synthetic data สำหรับ behaviors ที่มี data น้อย

**Phase 2 — Feedback Loop:**
- CEO reassignment → auto-labeled
- เก็บ implicit feedback (department reassign rate ฯลฯ)

**Phase 3 — Active Learning:**
- confidence < 90% but > 70% → สุ่ม sample เพื่อให้ human label
- เพิ่ม diversity ของ training data

### 6.3 Evaluation Framework

| Evaluation | Method | Target | When |
|:-----------|:-------|:------|:-----|
| **Offline Accuracy** | Hold-out test set (20% of labeled data) | ≥ 90% | Pre-launch |
| **Precision per behavior** | Per-class F1 score | ≥ 0.85 | Pre-launch |
| **False Positive Rate** | Misrouted / total requests | < 5% | Pre-launch |
| **CEO Review Volume** | % of requests requiring CEO review | < 10% | Post-launch |
| **Latency P95** | Time for classification | < 100ms | Post-launch |

---

## 7. Implementation Plan

### Phase 1: Data Schema Foundation (Week 1)

| Day | Task | Owner |
|:----|:-----|:------|
| 1-2 | Design & validate behavior taxonomy schema | Architect |
| 2-3 | Design training data & classification result schema | Architect |
| 3-4 | Create SQLite tables in Central Bus | Engineering |
| 4-5 | Migration script — add new tables without breaking existing | Engineering |

**Deliverable:** Central Bus schema v0.7 with behavior taxonomy + training data tables

### Phase 2: Taxonomy & Training Data (Week 2)

| Day | Task | Owner |
|:----|:-----|:------|
| 1-2 | Finalize 26 behavior definitions with examples | Product + Architect |
| 2-4 | Create seed training data (50 samples per behavior) | Product + QA |
| 4-5 | Validate taxonomy mapping — test with 100 historical requests | QA |

**Deliverable:** behavior_taxonomy.json + seed training dataset

### Phase 3: Classifier Implementation (Week 3)

| Day | Task | Owner |
|:----|:-----|:------|
| 1-3 | Build embedding + classifier pipeline | Engineering |
| 3-4 | Implement confidence scoring + threshold gate | Engineering |
| 4-5 | Implement CEO review queue UI/API | Engineering |

**Deliverable:** Behavior classifier integrated with Central Bus

### Phase 4: Integration & Testing (Week 4)

| Day | Task | Owner |
|:----|:-----|:------|
| 1-2 | Integration test — behavior classifier + existing routing | QA |
| 2-3 | A/B test — accuracy comparison vs existing routing | QA |
| 3-4 | Monitoring dashboard setup | Architect |
| 4-5 | Bug fixes + UAT | Engineering + Product |

**Deliverable:** Production-ready behavior-centric routing

---

## 8. In Scope

- 26-behavior taxonomy design and implementation
- Data schema for taxonomy, training data, classification results
- Embedding + linear classifier for intent classification
- Confidence scoring with 90% threshold
- CEO review queue for low-confidence requests
- Feedback loop — CEO reassignment → training data
- Monitoring dashboard for routing accuracy
- Integration test + A/B test framework

## 9. Out of Scope

- ❌ **Replacing existing Tier 1-3 routing** — behavior layer is additive
- ❌ **LLM-based classifier** — embedding approach is sufficient for launch
- ❌ **Real-time model retraining** — batch retrain only
- ❌ **Full multi-language NLP pipeline** — seed with Thai + English
- ❌ **Explainability UI** — nice to have in v1.1
- ❌ **Auto-retrain pipeline** — nice to have in v1.1

---

## 10. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|
| Seed training data ไม่พอ | Medium | High | Synthetic data generation + data augmentation |
| Thai language accuracy ต่ำ | Medium | High | ใช้ multilingual embedding + Thai-specific tokenizer |
| False positive สูง | Low | High | Conservative threshold (90%) + CEO review queue |
| ตลอด migration ส่งผลกระทบ | Low | Medium | Add-on approach — rollback ได้ทันที |
| Behavior taxonomy ไม่ครอบคลุม | Low | Medium | 26 behaviors expandable — version schema |

---

## 11. Dependencies

| Dependency | Department | Timeline |
|:-----------|:-----------|:---------|
| Central Bus SQLite backend | Architect | ✅ Existing |
| RoutingEngine framework | Architect | ✅ Existing |
| CEO Review Queue UI | Engineering | Week 3 |
| Monitoring Dashboard | Architect | Week 4 |
| Training data labeling | Product + QA | Week 2 |

---

## 12. Open Questions

1. **Embedding model specific:** `sentence-transformers` vs `fasttext` vs custom? — รอ Engineering feasibility check
2. **CEO Review Queue:** dashboard in Central Bus หรือ Slack notification? — รอ CEO preference
3. **Cold start:** จะทำอย่างไรใน 2-3 วันแรกก่อนมี seed data เพียงพอ? — Proposal: เปิดเฉพาะ monitoring ก่อน (classify แต่ไม่ route)
4. **Periodic retrain:** retrain ทุกคืนหรือทุกสัปดาห์? — Proposal: nightly batch retrain

---

## 13. Success Metrics

*(รายละเอียดอยู่ใน section แยกด้านล่าง — ดู Success Metrics)*

---

**PRD Prepared by:** Product (โปรดัค)
**Reviewed by:** Architect (พี่ทรงศักดิ์) — Pending schema design
**Approved by:** CEO (หนุมาน) ✅ — Key decisions finalized
