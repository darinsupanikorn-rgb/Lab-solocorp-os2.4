"""Watchdog cron — ตรวจสุขภาพระบบทุก 5 นาที

ตรวจ 4 อย่าง:
  1. ประมวลผลข้อความในคิว (watchdog_loop)
  2. dead letters (ข้อความตายจริง)
  3. orphaned messages — ข้อความที่ค้างและไม่มีใครจะมารับ (กันตายเงียบ)
  4. LLM model health — โมเดลใน fallback chain ยังมีอยู่จริงไหม
     (ถ้าหาย → agent 19 ตัวจะ "ตาบอด" โดยไม่มี error ชัดเจน)
"""
import json
import os
import sys
import time
import urllib.request

from central_bus.monitor_watchdog import (
    watchdog_loop,
    check_dead_letters,
    check_orphaned_messages,
    check_model_health,
)

BUS_URL = os.environ.get("SOLOCORP_BUS_URL", "http://127.0.0.1:8099")
API_KEY = os.environ.get("SOLOCORP_API_KEY", "sk-solocorp-admin-local-dev-001")


def _report_to_ceo(summary: str, details: dict, status: str = "failed") -> bool:
    """ส่งรายงานเข้า ceo_alerts ผ่าน Bus (action=report_back → bus ปิดสถานะให้)"""
    body = json.dumps({
        "source_agent": "watchdog",
        "task_id": f"watchdog-model-health-{int(time.time())}",
        "target_agent": "ceo-hanuman",
        "payload": {
            "action": "report_back",
            "status": status,
            "summary": summary,
            "details": details,
        },
    }, ensure_ascii=False).encode()
    req = urllib.request.Request(
        f"{BUS_URL}/v1/observe",
        data=body,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10).read()
        return True
    except Exception as e:
        print(f"[WARN] ส่งรายงาน CEO ไม่สำเร็จ: {e}", file=sys.stderr)
        return False

processed = watchdog_loop(max_iterations=5)
stuck = check_dead_letters()
orphans = check_orphaned_messages()
models = check_model_health()

if processed > 0:
    print(f"[OK] Watchdog processed {processed} messages")

if stuck:
    print(f"[WARN] Dead letters: {len(stuck)} stuck messages")
    for item in stuck[-3:]:
        print(f"   - {item.get('reason', 'unknown')}: "
              f"{item.get('message', {}).get('trace_id', '?')[:20]}")

failed = False

if orphans:
    failed = True
    print(f"[WARN] Orphaned messages: {len(orphans)} ค้างและไม่มีใครรับ")
    for o in orphans[-5:]:
        print(f"   - {o['id'][:8]} status={o['status']} "
              f"target={o['target_agent']} — {o['reason']}")
    print("[WARN] แก้: ตั้ง target_agent ให้เป็น agent_id ที่ลงทะเบียน "
          "(ดู workers/agent_worker_service.py AGENT_IDS) หรือล้างด้วย "
          "scripts/purge-stale-queue.py")

# ── LLM model health ──────────────────────────────────────────────────
if models.get("skipped"):
    print(f"[INFO] ข้าม model health check: {models.get('error')}")
elif not models.get("ok", True):
    failed = True
    missing = models.get("missing", [])
    print(f"[WARN] LLM chain มีโมเดลที่หายไป {len(missing)} ตัว: {missing}")
    print("[WARN] agent ทั้ง 19 ตัวจะ 'ตาบอด' (ไม่มี error ชัดเจน) — "
          "แก้ workers/llm_provider.py MODEL_FALLBACKS")
    _report_to_ceo(
        summary=f"🚨 LLM fallback chain มีโมเดลที่ไม่มีจริง: {', '.join(missing)}",
        details={
            "missing": missing,
            "chain": models.get("chain", []),
            "usable": models.get("usable", []),
            "checked_at": models.get("checked_at"),
        },
        status="failed",
    )
else:
    usable = models.get("usable", [])
    print(f"[OK] LLM chain ปกติ ({len(usable)}/{len(models.get('chain', []))} "
          f"โมเดลใช้ได้)")
    candidates = models.get("candidates", [])
    if candidates:
        print(f"[INFO] โมเดลใหม่ที่ยังไม่อยู่ใน chain ({len(candidates)}): "
              f"{candidates[:5]}{'...' if len(candidates) > 5 else ''}")
        print("[INFO] ทดสอบก่อนเพิ่ม: python scripts/check-model-health.py --verify <model>")

if failed:
    sys.exit(1)  # ให้ cron log เห็นเป็น error → เห็นง่ายขึ้น
