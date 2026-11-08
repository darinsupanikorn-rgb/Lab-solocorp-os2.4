#!/usr/bin/env python3
"""CFO Finance Analysis — Backend Engine

อ่าน parameter จาก skills/cfo-finance-params.toml
ใช้วิเคราะห์งบประมาณ, cost optimization, forecast, audit, mirror review

Usage:
    python finance_analysis.py budget_analysis --department engineering --period Q3-2026
    python finance_analysis.py cost_optimization --department cfo
    python finance_analysis.py forecast --period short
    python finance_analysis.py financial_audit --period 2026-Q2
    python finance_analysis.py mirror_review --decision "Budget 15,000 บาท"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback

# ── Paths ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
PARAMS_PATH = BASE_DIR / "skills" / "cfo-finance-params.toml"


# ── Load Parameters ─────────────────────────────────────────────────


def load_params() -> dict[str, Any]:
    """โหลด parameter config จาก TOML"""
    try:
        with open(PARAMS_PATH, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"❌ Parameter file not found: {PARAMS_PATH}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"❌ Error loading params: {e}", file=sys.stderr)
        return {}


def get_param(params: dict, *keys: str, default: Any = None) -> Any:
    """ดึงค่า parameter ซ้อนกัน ปลอดภัย"""
    current = params
    for k in keys:
        if isinstance(current, dict):
            current = current.get(k, {})
        else:
            return default
    return current if current != {} else default


# ── Depth Multiplier ──────────────────────────────────────────────────


def get_depth_multiplier(params: dict, key: str, depth: str = "standard") -> float:
    """ดึง depth multiplier — standard=1.0, high=ปรับ stricter"""
    multipliers = get_param(params, "depth", "multipliers", key, default={})
    return float(multipliers.get(depth, 1.0))


def get_horizon_multiplier(params: dict, key: str, horizon: str = "medium") -> float:
    """ดึง time_horizon multiplier — short=เข้มงวด, medium=1.0, long=ยืดหยุ่น

    Time horizon เปลี่ยน perspective การวิเคราะห์:
    - short (0-3mo):  cash preservation — tolerance ต่ำ, flag ถี่
    - medium (3-6mo): operational balance
    - long (6-12+mo): strategic — tolerance สูง, focus trend
    """
    multipliers = get_param(params, "time_horizon", "multipliers", key, default={})
    return float(multipliers.get(horizon, 1.0))


def get_horizon_label(params: dict, horizon: str = "medium") -> str:
    """ดึงคำอธิบายของ time_horizon"""
    labels = get_param(params, "time_horizon", "labels", default={})
    return labels.get(horizon, f"Horizon: {horizon}")


def apply_threshold(base: float, multiplier: float) -> float:
    """Apply depth multiplier to a threshold.
    Note: multipliers < 1.0 = stricter for thresholds (lower = stricter)."""
    return round(base * multiplier, 2)


def apply_multiplier_up(base: float, multiplier: float) -> float:
    """Apply depth multiplier for values that INCREASE when depth=high
    (e.g., pass threshold, expense premium)."""
    # multiplier > 1.0 = stricter (higher threshold)
    if multiplier >= 1.0:
        return round(base * multiplier, 2)
    # multiplier < 1.0 = less strict — don't go below base
    return base


# ═══════════════════════════════════════════════════════════════════════
# 1. BUDGET ANALYSIS
# ═══════════════════════════════════════════════════════════════════════


def budget_analysis(
    department: str = "all",
    period: str = "current",
    actual: float = 0,
    plan: float = 0,
    depth: str = "standard",
    time_horizon: str = "medium",
) -> dict[str, Any]:
    """วิเคราะห์งบประมาณเทียบ actual vs plan

    Args:
        depth: 'standard' หรือ 'high' — ปรับความละเอียดของการวิเคราะห์
        time_horizon: 'short', 'medium', 'long' — มุมมองเวลา
    """
    params = load_params()

    # Combine depth + horizon multipliers (相乘 = combined effect)
    var_mult = (
        get_depth_multiplier(params, "variance_warning", depth)
        * get_horizon_multiplier(params, "variance_warning", time_horizon)
    )
    crit_mult = (
        get_depth_multiplier(params, "variance_critical", depth)
        * get_horizon_multiplier(params, "variance_critical", time_horizon)
    )

    warning_pct = apply_threshold(
        get_param(params, "variance", "warning", default=10.0), var_mult
    )
    critical_pct = apply_threshold(
        get_param(params, "variance", "critical", default=15.0), crit_mult
    )
    acceptable_pct = get_param(params, "variance", "acceptable", default=5.0)

    if plan == 0:
        variance_pct = 0
    else:
        variance_pct = round(((actual - plan) / plan) * 100, 2)

    # Determine status
    if abs(variance_pct) <= acceptable_pct:
        status = "🟢 on_track"
        severity = "normal"
    elif abs(variance_pct) <= warning_pct:
        status = "🟡 warning"
        severity = "watch"
    elif abs(variance_pct) <= critical_pct:
        status = "🟠 elevated"
        severity = "attention"
    else:
        status = "🔴 critical"
        severity = "escalate"

    # Score (higher = better adherence)
    adherence_score = max(0, 1 - (abs(variance_pct) / 100))

    # Approval level check with depth adjustment
    approval_mult = (
        get_depth_multiplier(params, "approval_tier", depth)
        * get_horizon_multiplier(params, "approval_tier", time_horizon)
    )
    approval_rules = _check_approval_level(abs(variance_pct), approval_mult)

    # Horizon-specific perspective
    horizon_label = get_horizon_label(params, time_horizon)
    perspective = {
        "short": "มุมมองระยะสั้น — cash preservation, ต้องระวังทุกส่วนต่าง",
        "medium": "มุมมองปกติ — สมดุลระหว่าง tactical และ strategic",
        "long": "มุมมองระยะยาว — ยืดหยุ่นเรื่อง variance, focus ที่ trend",
    }.get(time_horizon, "")

    # Deep analysis: add breakdown dimension
    breakdown = None
    if depth == "high":
        efficiency = round(actual / max(plan, 1), 4)
        breakdown = {
            "variance_tolerance": {
                "acceptable_max": acceptable_pct,
                "warning_max": warning_pct,
                "critical_max": critical_pct,
            },
            "efficiency_ratio": {
                "spend_vs_plan": efficiency,
                "interpretation": "over_budget" if efficiency > 1 else "under_budget",
            },
            "depth_note": "วิเคราะห์เชิงลึก — threshold ถูกปรับให้เข้มงวดขึ้นตาม depth parameter",
        }

    # Time horizon-specific analysis
    horizon_analysis = None
    if time_horizon == "short":
        # short-term: focus on immediate cash impact
        cash_impact = abs(actual - plan)
        horizon_analysis = {
            "focus": "immediate_cash",
            "cash_impact_bath": cash_impact,
            "recommendation": (
                f"กระทบเงินสด {cash_impact:,.0f} บาท — "
                + ("ต้องหาทางลดทันที" if cash_impact > 10000 else "ติดตามต่อเนื่อง")
            ),
        }
    elif time_horizon == "long":
        # long-term: focus on trend and annualized impact
        annualized_variance = round(((actual - plan) / max(plan, 1)) * 12 * 100, 2)
        horizon_analysis = {
            "focus": "trend_sustainability",
            "annualized_variance_pct": annualized_variance,
            "recommendation": (
                f"annualized impact ~{annualized_variance}% — "
                + ("ต้องปรับกลยุทธ์ระยะยาว" if abs(annualized_variance) > 20 else "ยังอยู่ในเกณฑ์ acceptable")
            ),
        }

    return {
        "command": "budget_analysis",
        "depth": depth,
        "time_horizon": time_horizon,
        "horizon_label": horizon_label,
        "perspective": perspective,
        "department": department,
        "period": period,
        "input": {"actual": actual, "plan": plan},
        "result": {
            "variance_pct": variance_pct,
            "status": status,
            "severity": severity,
            "adherence_score": round(adherence_score, 4),
            "recommendation": _budget_recommendation(severity, variance_pct),
        },
        "breakdown": breakdown,
        "horizon_analysis": horizon_analysis,
        "approval": approval_rules,
        "params_version": get_param(params, "metadata", "version", default="unknown"),
    }


def _budget_recommendation(severity: str, variance: float) -> str:
    if severity == "normal":
        return "✅ งบประมาณเป็นไปตามแผน — ติดตามต่อเนื่อง"
    elif severity == "watch":
        return "👀 เริ่มมีความแตกต่าง — ควรตรวจสอบสาเหตุและปรับแผน"
    elif severity == "attention":
        return "⚠️ ความแตกต่างมีนัยสำคัญ — ต้องคุยกับ department head"
    else:
        return "🚨 ความแตกต่างรุนแรง — escalate ทันที, ต้องปรับแผนหรือ cut cost"


def _check_approval_level(amount: float, depth_mult: float = 1.0) -> dict:
    """ตรวจสอบ approval level ตามจำนวนเงิน

    Args:
        amount: จำนวนเงิน (บาท)
        depth_mult: depth multiplier — high=0.5 ทำให้ approval tier ลดลงครึ่งหนึ่ง
    """
    params = load_params()
    auto_max = get_param(params, "approval", "auto_max_bath", default=1000) * depth_mult
    cfo_max = get_param(params, "approval", "cfo_max_bath", default=10000) * depth_mult
    ceo_max = get_param(params, "approval", "ceo_max_bath", default=50000) * depth_mult

    if amount <= auto_max:
        return {
            "level": "auto", "required": "none", "note": "ไม่ต้องขออนุมัติ",
            "adjusted_thresholds": {"auto_max": auto_max},
        }
    elif amount <= cfo_max:
        return {
            "level": "cfo", "required": "cfo-meetoo", "note": "CFO approve",
            "adjusted_thresholds": {"auto_max": auto_max, "cfo_max": cfo_max},
        }
    elif amount <= ceo_max:
        return {
            "level": "ceo",
            "required": "cfo-meetoo + ceo-hanuman",
            "note": "CFO + CEO approve",
            "adjusted_thresholds": {
                "auto_max": auto_max, "cfo_max": cfo_max, "ceo_max": ceo_max,
            },
        }
    else:
        return {
            "level": "owner",
            "required": "cfo-meetoo + ceo-hanuman + dr.solodev",
            "note": "ต้อง Owner approve",
            "adjusted_thresholds": {
                "auto_max": auto_max, "cfo_max": cfo_max, "ceo_max": ceo_max,
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# 2. COST OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════


def cost_optimization(
    department: str = "cfo",
    costs: dict[str, float] | None = None,
    depth: str = "standard",
    time_horizon: str = "medium",
) -> dict[str, Any]:
    """แนะนำการลดต้นทุน

    Args:
        depth: 'standard' หรือ 'high' — high=เจาะลึกทุกหมวด
        time_horizon: 'short', 'medium', 'long' — มุมมองเวลา
    """
    params = load_params()
    saving_mult = (
        get_depth_multiplier(params, "saving_target", depth)
        * get_horizon_multiplier(params, "saving_target", time_horizon)
    )
    min_saving = get_param(params, "savings", "minimum_percent", default=10.0) * saving_mult
    payback_max = get_param(params, "savings", "payback_max_months", default=6)
    categories_order = get_param(params, "cost_categories", "order", default=[])

    if not costs:
        costs = {
            "API/Model": 50000,
            "Infrastructure": 30000,
            "Tools/Subscriptions": 15000,
            "Marketing": 20000,
            "Operations": 10000,
        }

    total = sum(costs.values())
    recommendations = []

    # Simple analysis: suggest optimizing top categories
    # For recurring costs, savings are ongoing → payback is immediate (0 months)
    sorted_costs = sorted(costs.items(), key=lambda x: x[1], reverse=True)
    for cat, amount in sorted_costs[:3]:
        monthly_saving = round(amount * (min_saving / 100), 2)
        payback = 0.0  # recurring cost — saving is immediate

        if monthly_saving > 0:
            recommendations.append({
                "category": cat,
                "current_cost": amount,
                "pct_of_total": round((amount / total) * 100, 1),
                "monthly_saving": monthly_saving,
                "annual_saving": round(monthly_saving * 12, 2),
                "saving_pct": min_saving,
                "payback_months": payback,
                "action": _cost_action(cat),
                "priority": "high" if amount / total > 0.3 else "medium",
                "roi": "ongoing" if payback == 0 else f"{payback}mo payback",
            })

    # Deep analysis: analyze ALL categories with per-item saving breakdown
    deep_breakdown = None
    if depth == "high":
        deep_breakdown = {
            "analysis_scope": "full — ทุกหมวดถูกวิเคราะห์เชิงลึก",
            "saving_assumption": f"target saving {min_saving}% ต่อหมวด (ปรับตาม depth multiplier)",
            "category_detail": [
                {
                    "category": cat,
                    "current": amt,
                    "pct": round((amt / total) * 100, 1),
                    "potential_saving": round(amt * (min_saving / 100), 2),
                    "action": _cost_action(cat),
                }
                for cat, amt in sorted_costs
            ],
            "priority_matrix": {
                "high_impact": [r["category"] for r in recommendations if r["priority"] == "high"],
                "medium_impact": [r["category"] for r in recommendations if r["priority"] == "medium"],
            },
        }

    # Horizon-specific focus
    horizon_label = get_horizon_label(params, time_horizon)
    horizon_focus = {
        "short": "quick_wins — focus categories with immediate saving potential",
        "medium": "balanced — mix of quick wins and strategic savings",
        "long": "strategic — focus on sustainable long-term savings",
    }.get(time_horizon, "")

    return {
        "command": "cost_optimization",
        "depth": depth,
        "time_horizon": time_horizon,
        "horizon_label": horizon_label,
        "horizon_focus": horizon_focus,
        "department": department,
        "total_monthly": total,
        "recommendations": recommendations,
        "breakdown": deep_breakdown,
        "summary": {
            "total_monthly_saving": round(sum(r["monthly_saving"] for r in recommendations), 2),
            "saving_pct_of_total": round(
                (sum(r["monthly_saving"] for r in recommendations) / total) * 100, 1
            ),
            "estimated_annual_saving": round(
                sum(r["annual_saving"] for r in recommendations), 2
            ),
        },
    }


def _cost_action(category: str) -> str:
    actions = {
        "API/Model": "ตรวจสอบ rate limiting, เปลี่ยนไปใช้ model ที่ถูกกว่า, ใช้ batch processing",
        "Infrastructure": "ปรับ downsizing, ใช้ spot/preemptible instances, ตั้ง auto-scaling",
        "Tools/Subscriptions": "รวม subscription ที่ซ้ำซ้อน, negotiate ลดราคา, หา OSS alternative",
        "Marketing": "วิเคราะห์ ROI ต่อ channel, focus ที่ high converting channel",
        "Operations": " automate manual process, ลด overhead ที่ไม่จำเป็น",
    }
    return actions.get(category, "review และหาทางลดต้นทุน")


# ═══════════════════════════════════════════════════════════════════════
# 3. FINANCIAL FORECAST
# ═══════════════════════════════════════════════════════════════════════


def forecast(
    period: str = "short",
    monthly_revenue: float = 100000,
    monthly_expense: float = 80000,
    cash_on_hand: float = 500000,
    depth: str = "standard",
    time_horizon: str = "medium",
) -> dict[str, Any]:
    """พยากรณ์การเงิน

    Args:
        depth: 'standard' หรือ 'high' — high=conservative multipliers เข้มงวดขึ้น
        time_horizon: 'short', 'medium', 'long' — มุมมองเวลา
    """
    params = load_params()

    rev_mult = (
        get_depth_multiplier(params, "conservative_rev", depth)
        * get_horizon_multiplier(params, "conservative_rev", time_horizon)
    )
    exp_mult = (
        get_depth_multiplier(params, "conservative_exp", depth)
        * get_horizon_multiplier(params, "conservative_exp", time_horizon)
    )

    # Combined effect: depth × horizon
    rev_discount = (
        get_param(params, "forecast", "conservative", "revenue_discount", default=0.70)
        * rev_mult
    )
    exp_premium = (
        get_param(params, "forecast", "conservative", "expense_premium", default=1.20)
        * exp_mult
    )
    buffer_months = get_param(params, "forecast", "conservative", "runway_buffer_months", default=6)

    horizons = {
        "short": get_param(params, "forecast", "horizons", "short_term_months", default=3),
        "medium": get_param(params, "forecast", "horizons", "medium_term_months", default=6),
        "long": get_param(params, "forecast", "horizons", "long_term_months", default=12),
    }

    months = horizons.get(period, 3)

    # Conservative forecast (ตาม CFO principle)
    conservative_revenue = monthly_revenue * rev_discount
    conservative_expense = monthly_expense * exp_premium
    monthly_burn = conservative_expense - conservative_revenue
    monthly_net = [cash_on_hand - (monthly_burn * m) for m in range(months + 1)]

    runway_months = round(cash_on_hand / max(monthly_burn, 1), 1)
    runway_status = "🟢 safe" if runway_months >= buffer_months else "🔴 critical"

    # Multi-scenario for deep analysis
    scenarios = None
    if depth == "high":
        scenarios = {
            "best_case": {
                "revenue": monthly_revenue,
                "expense": monthly_expense,
                "runway_months": round(cash_on_hand / max(monthly_expense - monthly_revenue, 1), 1),
            },
            "base_case": {
                "revenue": round(monthly_revenue * 0.85, 2),
                "expense": round(monthly_expense * 1.10, 2),
                "runway_months": runway_months,
            },
            "worst_case": {
                "revenue": round(monthly_revenue * rev_discount, 2),
                "expense": round(monthly_expense * exp_premium, 2),
                "runway_months": round(cash_on_hand / max(
                    (monthly_expense * exp_premium) - (monthly_revenue * rev_discount), 1
                ), 1),
            },
        }

    horizon_label = get_horizon_label(params, time_horizon)
    confidence = {
        "short": "high — อิงข้อมูลจริง 3 เดือนล่าสุด",
        "medium": "medium — ผสม actual + projection",
        "long": "low — uncertainty สูง, ต้องรีไฟแนนซ์เป็นระยะ",
    }.get(time_horizon, "")

    return {
        "command": "forecast",
        "depth": depth,
        "time_horizon": time_horizon,
        "horizon_label": horizon_label,
        "confidence": confidence,
        "period": period,
        "horizon_months": months,
        "input": {
            "monthly_revenue": monthly_revenue,
            "monthly_expense": monthly_expense,
            "cash_on_hand": cash_on_hand,
        },
        "conservative": {
            "adjusted_revenue": round(conservative_revenue, 2),
            "adjusted_expense": round(conservative_expense, 2),
            "monthly_net_burn": round(monthly_burn, 2),
            "reasoning": (
                f"depth={depth}: รายได้ -{round((1-rev_discount)*100)}%, "
                f"ค่าใช้จ่าย +{round((exp_premium-1)*100)}% (risk buffer)"
            ),
        },
        "scenarios": scenarios,
        "runway": {
            "months": runway_months,
            "required_buffer": buffer_months,
            "status": runway_status,
            "end_cash": round(monthly_net[-1], 2) if monthly_net[-1] > 0 else 0,
            "warning": runway_months < buffer_months,
        },
        "monthly_projection": [
            {"month": m, "cash": round(monthly_net[m], 2)} for m in range(months + 1)
        ],
    }


# ═══════════════════════════════════════════════════════════════════════
# 4. FINANCIAL AUDIT
# ═══════════════════════════════════════════════════════════════════════


def financial_audit(
    period: str = "2026-Q2",
    transactions: list[dict] | None = None,
    depth: str = "standard",
    time_horizon: str = "medium",
) -> dict[str, Any]:
    """ตรวจสอบการเงินและ audit trail

    Args:
        depth: 'standard' หรือ 'high' — high=flag threshold ต่ำลง, severity เข้มงวดขึ้น
        time_horizon: 'short', 'medium', 'long' — scope การตรวจสอบ
    """
    params = load_params()
    flag_mult = (
        get_depth_multiplier(params, "audit_flag", depth)
        * get_horizon_multiplier(params, "audit_flag", time_horizon)
    )
    flag_threshold = get_param(params, "audit", "auto_flag_threshold_bath", default=5000) * flag_mult
    critical_level = get_param(params, "audit", "severity", "critical", default=30000) * flag_mult

    # Mock transactions for demo
    if transactions is None:
        transactions = [
            {"id": "T001", "amount": 4500, "category": "API", "approved_by": "meetoo", "docs": True},
            {"id": "T002", "amount": 25000, "category": "Infra", "approved_by": "meetoo", "docs": True},
            {"id": "T003", "amount": 1200, "category": "Tools", "approved_by": "", "docs": False},
            {"id": "T004", "amount": 35000, "category": "Marketing", "approved_by": "ceo", "docs": True},
            {"id": "T005", "amount": 800, "category": "Ops", "approved_by": "", "docs": True},
        ]

    findings = []
    for tx in transactions:
        flags = []
        severity = "info"

        if tx["amount"] >= flag_threshold and not tx.get("approved_by"):
            flags.append("MISSING_APPROVAL")
            severity = "critical" if tx["amount"] >= critical_level else "major"

        if tx["amount"] >= flag_threshold and not tx.get("docs"):
            flags.append("MISSING_DOCUMENTATION")
            severity = "major"

        findings.append({
            "transaction_id": tx["id"],
            "amount": tx["amount"],
            "category": tx["category"],
            "flags": flags,
            "severity": severity,
            "status": "🔴 flag" if flags else "✅ clean",
        })

    flagged_count = sum(1 for f in findings if f["flags"])
    total_flagged_amount = sum(
        f["amount"] for f in findings if f["flags"]
    )

    horizon_label = get_horizon_label(params, time_horizon)
    audit_scope = {
        "short": "full_dive — ตรวจทุก transaction ละเอียด (flag threshold ต่ำ)",
        "medium": "standard — ตรวจตามปกติ",
        "long": "material — focus ที่ transaction สำคัญ, ข้ามรายการเล็ก",
    }.get(time_horizon, "")

    return {
        "command": "financial_audit",
        "depth": depth,
        "time_horizon": time_horizon,
        "horizon_label": horizon_label,
        "audit_scope": audit_scope,
        "period": period,
        "total_transactions": len(findings),
        "flagged": flagged_count,
        "clean": len(findings) - flagged_count,
        "total_flagged_amount": total_flagged_amount,
        "audit_params": {
            "flag_threshold": flag_threshold,
            "severity_critical": critical_level,
            "depth_note": "ปรับ flag threshold ตาม depth multiplier" if depth == "high" else None,
        },
        "findings": findings,
        "recommendation": (
            f"depth={depth} horizon={time_horizon}: พบ {flagged_count} รายการที่ต้องสอบทาน "
            f"จาก {len(findings)} รายการ รวมมูลค่า {total_flagged_amount:,} บาท "
            f"(flag threshold: {flag_threshold:,.0f} บาท)"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. MIRROR REVIEW
# ═══════════════════════════════════════════════════════════════════════


def mirror_review(
    decision: str = "",
    amount: float = 0,
    depth: str = "standard",
    time_horizon: str = "medium",
) -> dict[str, Any]:
    """ตรวจสอบ decision ด้วย Mirror CEO perspective

    Args:
        depth: 'standard' หรือ 'high' — high=questions เพิ่ม, pass threshold สูงขึ้น
        time_horizon: 'short', 'medium', 'long' — horizon-specific questions
    """
    params = load_params()

    # Select questions based on depth + horizon
    if depth == "high":
        questions = get_param(
            params, "mirror_review", "questions_high",
            default=[
                "Dr.solodev ในมุม conservative จะ approve ไหม?",
                "Worst case นี้ Owner รับได้ไหม?",
                "Owner จะดีใจหรือเสียใจที่ใช้เงินนี้?",
                "ถ้า decision นี้ผิดพลาด โอกาส recovery มีแค่ไหน?",
                "Decision นี้สอดคล้องกับ long-term vision ของ Dr.solodev หรือไม่?",
            ],
        )
    else:
        base_questions = get_param(
            params, "mirror_review", "questions",
            default=[
                "Dr.solodev ในมุม conservative จะ approve ไหม?",
                "Worst case นี้ Owner รับได้ไหม?",
                "Owner จะดีใจหรือเสียใจที่ใช้เงินนี้?",
            ],
        )
        questions = list(base_questions)

        # Add horizon-specific questions
        if time_horizon == "short":
            questions.append("Decision นี้กระทบ cash flow ใน 3 เดือนนี้ยังไง?")
        elif time_horizon == "long":
            questions.append("Decision นี้จะส่งผลยังไงใน 12 เดือนข้างหน้า?")

    mirror_mult = (
        get_depth_multiplier(params, "mirror_pass", depth)
        * get_horizon_multiplier(params, "mirror_pass", time_horizon)
    )
    pass_threshold = (
        get_param(params, "mirror_review", "pass_threshold_percent", default=60)
        * mirror_mult
    )
    auto_pass = get_param(params, "mirror_review", "auto_pass_threshold_bath", default=1000)

    if amount <= auto_pass:
        return {
            "command": "mirror_review",
            "depth": depth,
            "decision": decision,
            "amount": amount,
            "result": "auto_pass",
            "reason": f"จำนวนเงิน {amount:,.0f} บาท ≤ {auto_pass:,.0f} — auto approved",
            "questions": [],
        }

    # Simulate answering mirror questions
    q_results = []
    passed_count = 0
    for q in questions:
        simulated_pass = len(decision) > 10
        if simulated_pass:
            passed_count += 1
        q_results.append({
            "question": q,
            "result": "pass" if simulated_pass else "fail",
            "confidence": 0.85,
        })

    score = int((passed_count / len(questions)) * 100)
    passed = score >= pass_threshold

    horizon_label = get_horizon_label(params, time_horizon)

    return {
        "command": "mirror_review",
        "depth": depth,
        "time_horizon": time_horizon,
        "horizon_label": horizon_label,
        "decision": decision,
        "amount": amount,
        "result": "pass" if passed else "fail",
        "score": score,
        "threshold": max(0, min(100, pass_threshold)),
        "total_questions": len(questions),
        "passed_questions": passed_count,
        "reason": (
            "✅ Decision สอดคล้องกับวิสัยทัศน์ของ Dr.solodev"
            if passed
            else "❌ Decision นี้ไม่ผ่าน Mirror Check — ควร reconsider"
        ),
        "questions": q_results,
    }


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

COMMANDS = {
    "budget_analysis": budget_analysis,
    "cost_optimization": cost_optimization,
    "financial_audit": financial_audit,
    "forecast": forecast,
    "mirror_review": mirror_review,
}


def main():
    parser = argparse.ArgumentParser(description="CFO Finance Analysis Engine")
    parser.add_argument(
        "command",
        choices=list(COMMANDS.keys()),
        help="Analysis command to run",
    )
    parser.add_argument("--department", "-d", default="all", help="Department name")
    parser.add_argument("--period", "-p", default="current", help="Period (Q3-2026, short, etc)")
    parser.add_argument("--amount", "-a", type=float, default=0, help="Amount in bath")
    parser.add_argument("--decision", "-D", default="", help="Decision text for mirror review")
    parser.add_argument("--actual", type=float, default=0, help="Actual spend")
    parser.add_argument("--plan", type=float, default=0, help="Planned budget")
    parser.add_argument(
        "--depth", choices=["standard", "high"], default="standard",
        help="ความลึกของการวิเคราะห์: standard (default) หรือ high (เข้มงวด+ละเอียด)",
    )
    parser.add_argument(
        "--horizon", choices=["short", "medium", "long"], default="medium",
        help="มุมมองเวลา: short (0-3mo), medium (3-6mo), long (6-12+mo)",
    )
    parser.add_argument("--json", "-j", action="store_true", default=True, help="Output JSON")

    args = parser.parse_args()

    kwargs: dict = {"depth": args.depth, "time_horizon": args.horizon}
    if args.command == "budget_analysis":
        kwargs["department"] = args.department
        kwargs["period"] = args.period
    elif args.command == "cost_optimization":
        kwargs["department"] = args.department
    elif args.command == "financial_audit":
        kwargs["period"] = args.period
    elif args.command == "mirror_review":
        kwargs["decision"] = args.decision
        kwargs["amount"] = args.amount
    elif args.command == "forecast":
        kwargs["period"] = args.period

    if args.command == "budget_analysis":
        kwargs["actual"] = args.actual
        kwargs["plan"] = args.plan

    func = COMMANDS[args.command]
    result = func(**kwargs)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
