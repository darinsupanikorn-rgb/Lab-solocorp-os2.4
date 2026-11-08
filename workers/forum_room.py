#!/usr/bin/env python3
"""🏛️ forum_room.py — SoloCorp OS Forum Room (ฝั่ง OpenCode)

Port จาก Hermes `forum_room/prompt.md` — ตัวจัดเวทีตกผลึก ไม่ใช่ผู้สั่งงาน

หลักการ (ล็อกจาก Owner):
  1. ห้องไม่ลงมือทำ — ผลิตแค่มุมมอง (ideas/ข้อเสนอ/ข้อกังวล) สายงานตัวเอง
  2. CEO โยนแผน+เป้าหมายลงกลางห้อง → แจกขนานทุกมุม
  3. รับหมด กรองทีหลัง — รอบแรกห้ามวิจารณ์ข้ามทีม
  4. ตกผลึก 2 ชั้น — ชั้น 1 ห้องปั่น synthesis / ชั้น 2 CEO+Owner ย่อยด้วยกัน

สถาปัตยกรรม: คิดด้วย OpenCode (workers think → opencode CLI),
จำด้วยไฟล์ (bus/forum/<id>/ + bus/inbox), Bus เป็นสมุดบัญชี (ไม่พึ่ง busd)

ใช้:
  python -m workers.forum_room --topic "..." --goal "..." --depts legal,sales,product --timeout 180
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FORUM_DIR = REPO_ROOT / "bus" / "forum"
SEQ_FILE = FORUM_DIR / "sequence.txt"

SOUL_MAP = {
    "ceo": "profiles/01-ceo/SOUL.md",
    "coo": "profiles/02-coo/SOUL.md",
    "cfo": "profiles/02-cfo/SOUL.md",
    "cmo": "profiles/03-cmo/SOUL.md",
    "orchestrator": "profiles/04-orchestrator/SOUL.md",
    "architect": "profiles/05-architect/SOUL.md",
    "product": "profiles/06-product/SOUL.md",
    "engineering": "profiles/07-engineering/SOUL.md",
    "design": "profiles/08-design/SOUL.md",
    "ui-designer": "profiles/09-ui-designer/SOUL.md",
    "qa": "profiles/10-qa/SOUL.md",
    "sales": "profiles/11-sales/SOUL.md",
    "support": "profiles/12-support/SOUL.md",
    "legal": "profiles/13-legal/SOUL.md",
    "web3": "profiles/14-web3/SOUL.md",
    "content-creator": "profiles/15-content-creator/SOUL.md",
    "neteng": "profiles/16-neteng/SOUL.md",
    "cybersec": "profiles/17-cybersec/SOUL.md",
    "psychology": "profiles/18-psychology/SOUL.md",
}

FACILITATOR_RULES = """กติกาเวที Forum Room:
- ตอบสั้น กระชับ (ไม่เกิน 10 บรรทัด) ผูกกับมุมสายงานตัวเองเท่านั้น
- เสนอได้หมด: ไอเดีย ข้อเสนอ ข้อกังวล ความเสี่ยงที่เห็นจากมุมตัวเอง
- ห้ามวิจารณ์แผนกอื่น ห้ามเสนอแผนปฏิบัติการ (ห้องนี้ไม่ลงมือทำ)
- จบด้วย: จุดดี 1 ข้อ + จุดเสีย/เสี่ยง 1 ข้อ จากมุมตัวเอง"""


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def next_session_id() -> str:
    FORUM_DIR.mkdir(parents=True, exist_ok=True)
    n = int(SEQ_FILE.read_text(encoding="utf-8").strip() or "0") + 1 if SEQ_FILE.exists() else 1
    SEQ_FILE.write_text(str(n), encoding="utf-8")
    day = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d")
    return f"forum-{day}-{n:03d}"


def inbox(*argv: str) -> str:
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "inbox.py"), *argv],
        capture_output=True, text=True, timeout=30,
    )
    return (r.stdout + r.stderr).strip()


async def consult_dept(dept: str, topic: str, goal: str, timeout: int) -> dict:
    """ถาม 1 แผนก — คิดผ่าน BaseAgent.think (opencode CLI)"""
    from workers.agents.base_agent import BaseAgent

    soul_path = REPO_ROOT / SOUL_MAP[dept]
    agent = BaseAgent(agent_id=dept, name=dept, profile_path=soul_path)
    prompt = (
        f"เวที Forum Room — CEO วางแผน+เป้าหมายลงกลางห้อง:\n\n"
        f"แผน: {topic}\nเป้าหมาย: {goal}\n\n"
        f"{FACILITATOR_RULES}\n\n"
        f"จากมุมสายงานของเจ้า — เจ้าเห็นอะไร?"
    )
    try:
        text = await asyncio.wait_for(agent.think(prompt, max_tokens=600), timeout)
        ok = True
    except asyncio.TimeoutError:
        text = f"(หมดเวลา {timeout}s — ไม่ได้ความเห็น)"
        ok = False
    except Exception as e:  # noqa: BLE001
        text = f"(ผิดพลาด: {e})"
        ok = False
    return {"dept": dept, "ok": ok, "text": text, "at": now_iso()}


async def synthesize(topic: str, goal: str, insights: list[dict], timeout: int) -> str:
    from workers.agents.base_agent import BaseAgent

    ceo = BaseAgent(agent_id="ceo", name="CEO หนุมาน",
                    profile_path=REPO_ROOT / SOUL_MAP["ceo"])
    body = "\n\n".join(
        f"【{i['dept']}】\n{i['text']}" for i in insights
    )
    prompt = (
        f"เจ้าเป็นผู้จัดเวที Forum Room (ไม่ใช่ผู้ตัดสิน)\n"
        f"แผน: {topic}\nเป้าหมาย: {goal}\n\n"
        f"ความเห็นจากแต่ละมุม:\n{body}\n\n"
        f"ปั่นรวมเป็น synthesis: เก็บจุดดี ถอดจุดเสีย ชี้จุดที่แต่ละมุมขัดกัน "
        f"(ห้ามตัดสิน ห้ามเลือกข้าง — ส่งให้ CEO+Owner ย่อยชั้น 2 เอง)"
    )
    try:
        return await asyncio.wait_for(ceo.think(prompt, max_tokens=800), timeout)
    except Exception as e:  # noqa: BLE001
        return f"(synthesis ล้มเหลว: {e})"


async def run_forum(topic: str, goal: str, depts: list[str], timeout: int) -> Path:
    sid = next_session_id()
    sdir = FORUM_DIR / sid
    (sdir / "insights").mkdir(parents=True, exist_ok=True)
    meta = {"id": sid, "topic": topic, "goal": goal,
            "depts": depts, "started_at": now_iso()}
    (sdir / "proposal.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (sdir / "proposal.md").write_text(
        f"# {sid}\n\n## แผน\n{topic}\n\n## เป้าหมาย\n{goal}\n", encoding="utf-8")
    print(f"🏛️ เปิดเวที {sid}: {topic} (เชิญ {len(depts)} มุม: {', '.join(depts)})")

    # แจ้งทุกมุมผ่าน inbox (สมุดบัญชี)
    for d in depts:
        inbox("send", "ceo", d, f"[Forum {sid}] {topic}",
              f"เป้าหมาย: {goal}\n\nเชิญให้มุมมองจากสายงานเจ้า (สั้น กระชับ ไม่ต้องลงมือทำ)")

    # ถามขนาน ไม่รอคิว
    results = await asyncio.gather(
        *(consult_dept(d, topic, goal, timeout) for d in depts))
    insights = []
    for r in results:
        insights.append(r)
        (sdir / "insights" / f"{r['dept']}.md").write_text(
            f"# {r['dept']} @ {sid}\n\n{r['text']}\n", encoding="utf-8")
        inbox("send", r["dept"], "ceo", f"[Forum {sid}] insight จาก {r['dept']}", r["text"])
        mark = "✅" if r["ok"] else "⏱️"
        print(f"  {mark} {r['dept']}: ได้ความเห็นแล้ว")

    # ปั่นรวมชั้น 1 (ไม่ตัดสิน)
    synthesis = await synthesize(topic, goal, insights, timeout)
    (sdir / "synthesis.md").write_text(
        f"# Synthesis {sid} (ชั้น 1 — รอ CEO+Owner ย่อยชั้น 2)\n\n{synthesis}\n",
        encoding="utf-8")
    inbox("send", "ceo", "__human__", f"[Forum {sid}] synthesis พร้อม",
          f"เวที {sid} จบ — เชิญ Owner+CEO ย่อยชั้น 2 ที่ {sdir}")
    meta.update({"finished_at": now_iso(),
                 "ok": sum(1 for r in insights if r["ok"]),
                 "failed": sum(1 for r in insights if not r["ok"])})
    (sdir / "proposal.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ เวที {sid} จบ: {meta['ok']}/{len(depts)} มุมตอบ — synthesis ที่ {sdir}/synthesis.md")
    return sdir


def main() -> None:
    ap = argparse.ArgumentParser(prog="forum_room", description="SoloCorp OS Forum Room")
    ap.add_argument("--topic", required=True, help="แผนที่ CEO วางกลางห้อง")
    ap.add_argument("--goal", required=True, help="เป้าหมาย")
    ap.add_argument("--depts", required=True, help="คั่นด้วย comma เช่น legal,sales,product")
    ap.add_argument("--timeout", type=int, default=180, help="วินาทีต่อมุม (default 180)")
    args = ap.parse_args()
    depts = [d.strip() for d in args.depts.split(",") if d.strip()]
    bad = [d for d in depts if d not in SOUL_MAP]
    if bad:
        sys.exit(f"❌ แผนกไม่รู้จัก: {bad}")
    asyncio.run(run_forum(args.topic, args.goal, depts, args.timeout))


if __name__ == "__main__":
    main()
