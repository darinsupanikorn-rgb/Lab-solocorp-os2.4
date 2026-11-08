#!/usr/bin/env python3
"""🔑 SoloCorp OS — Generate Department API Keys

สร้าง API key ให้ทุก Agent ในระบบ — แต่ละกรมมี key ของตัวเอง

วิธีใช้:
    python3 scripts/generate-dept-keys.py
    python3 scripts/generate-dept-keys.py --dept cfo-meetoo   # เฉพาะกรมเดียว
    python3 scripts/generate-dept-keys.py --list              # ดู key ที่มีอยู่
"""

from __future__ import annotations

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from central_bus.db import ensure_db
from central_bus.api_keys import create_api_key, list_api_keys


# ── ข้อมูลทุก Agent ──────────────────────────────────────────────────
ALL_AGENTS = [
    # Phase 1 — Core
    ("cfo-meetoo", "02-cfo", "CFO — การเงิน"),
    ("architect-songsak", "05-architect", "Architect — สถาปัตยกรรม"),
    ("changful", "07-engineering", "Engineering — วิศวกรรม"),
    ("product-produck", "06-product", "Product — ผลิตภัณฑ์"),
    ("orchestrator-wut", "04-orchestrator", "Orchestrator — ประสานงาน"),
    # Phase 2 — Front
    ("cmo-mark", "03-cmo", "CMO — การตลาด"),
    ("design-kreet", "08-design", "Design — ออกแบบ"),
    ("qa", "10-qa", "QA — ทดสอบ"),
    ("sales", "11-sales", "Sales — ขาย"),
    ("support", "12-support", "Support — ลูกค้า"),
    # Phase 3 — Support
    ("legal-tulya", "13-legal", "Legal — กฎหมาย"),
    ("web3-aywa", "14-web3", "Web3 — บล็อกเชน"),
    ("content-creator-sek", "15-content-creator", "Content — คอนเทนต์"),
    ("neteng-neet", "16-neteng", "NetEng — เน็ตเวิร์ค"),
    ("cybersec-sai", "17-cybersec", "CyberSec — ความปลอดภัย"),
    # Phase 4 — Special
    ("psych-jit", "18-psychology", "Psychology — จิตวิทยา"),
    ("ui-designer", "09-ui-designer", "UI — อินเทอร์เฟซ"),
    ("rd-lab", "19-rd-lab", "R&D Lab — วิจัย"),
    # Admin
    ("ceo-hanuman", "01-ceo", "CEO — บริหารสูงสุด"),
]


async def generate_all(agent_filter: str | None = None):
    db = await ensure_db()

    print("=" * 70)
    print("  🔑 SoloCorp OS — Department API Keys Generator")
    print("=" * 70)

    for agent_id, dept_id, desc in ALL_AGENTS:
        if agent_filter and agent_filter != agent_id:
            continue

        result = await create_api_key(
            db,
            agent_id=agent_id,
            department_id=dept_id,
            department_name=desc,
            scope="dept",
            description=f"API key for {agent_id} ({desc})",
            created_by="ceo-hanuman",
        )

        full_key = result["full_key"]
        print(f"\n  📍 {agent_id:30s} [{dept_id}]")
        print(f"     🔑 {full_key}")
        print(f"     📋 Scope: {result['key_data']['scope']}")

    # Summary
    count = await db.fetch_one("SELECT COUNT(*) as cnt FROM api_keys WHERE enabled=1")
    print(f"\n{'='*70}")
    print(f"  ✅ Generated {count['cnt'] if count else 0} API keys")
    print(f"  💾 Stored in central_bus/bus.db")
    print(f"  {'='*70}")
    print()
    print("  วิธีใช้:")
    print("    export SOLOCORP_API_KEY=sk-cfo-meetoo-xxxx")
    print("    curl -H 'X-API-Key: $SOLOCORP_API_KEY' http://127.0.0.1:8099/v1/health")
    print()


async def list_existing():
    db = await ensure_db()
    keys = await list_api_keys(db)
    if not keys:
        print("  📭 No API keys found. Run without --list to generate.")
        return
    print(f"\n  🔑 Existing API keys ({len(keys)}):")
    for k in keys:
        status = "✅" if k["enabled"] else "❌"
        print(f"     {status} {k['key_prefix']:35s} → {k['department_name']:25s} [{k['scope']}]")


async def main():
    if "--list" in sys.argv:
        await list_existing()
        return

    agent_filter = None
    if "--dept" in sys.argv:
        idx = sys.argv.index("--dept")
        if idx + 1 < len(sys.argv):
            agent_filter = sys.argv[idx + 1]

    await generate_all(agent_filter)


if __name__ == "__main__":
    asyncio.run(main())
