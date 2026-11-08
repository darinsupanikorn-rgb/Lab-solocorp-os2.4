"""🤖 SoloCorp OS — LLM Provider

เชื่อมต่อ Agent กับ LLM (OpenCode ผ่าน opencode run CLI)

ใช้ opencode run CLI โดยตรง — stable, official, tested.
- ส่ง prompt ผ่าน stdin ป้องกัน shell injection
- ⚠️ ไม่มี --pure ในคำสั่ง — opencode v2.1.4 ไม่รู้จัก flag นี้ (unknown flag =
  ทุกโมเดลล้มทั้ง chain) ใช้เฉพาะ flag ที่ `opencode run --help` ระบุ
- บังคับ `--agent plan` (read-only) — subprocess ไม่มีใครกด "allow" ได้ ถ้าใช้ agent
  ที่มี shell/write โมเดลจะขอ permission แล้วค้าง → ไม่มีคำตอบทั้ง org
  override ได้ด้วย OPENCODE_AGENT
- retry + timeout + semaphore concurrency control
- ทุก call มี session id ของเราเอง (`--session ses_llm…`) → ตามรอย usage ได้
  จาก opencode.db และจาก console request logs (ดู workers/token_ledger.py)
- วัด token จริงต่อ call + เพดานรายวัน + quota lock (ไม่ยิงซ้ำเข้ากำแพง 429)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from workers import token_ledger

log = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────

# Fallback chain (2026-10-25 — วัดจริงจาก repo root ทุกตัว
# หลักฐาน: bus/evidence/2026-10-25/model-health/{names,quality,latency}.log):
# 1. DeepSeek V4.1 Flash Free  — ตัวหลัก · 15.1s · ไทย 1078 · ไม่เรียก tool
#    (latency สั้นสุด steadier สุด: 2.62/2.69/2.65s) · เคยเขียน draft ที่ผ่าน D2
# 2. Nemotron 3.5 Lightning    — 13.2s · ไทย 1087 · เร็วสุด/ไทยมากสุด
# 3. Nemotron 3 Ultra          — 19.0s · ไทย 702
# 4. Big Pickle                — 19.8s · ไทย 871
# 5. Mimo 2.6 Flash Free       — 82.9s + พยายามเรียก tool → เก็บไว้ท้ายสุดเท่านั้น
#
# ⚠️ ตายแล้ว upstream (2026-10-25 — "Model unavailable" จาก opencode v2.1.4)
#    → ย้ายเข้า DEAD_MODELS (caller เก่าที่ส่งชื่อนี้มาจะถูก map เข้า chain):
#    minimax-m3.1-flash-free (เคยเป็น DEFAULT_MODEL), longcat-2.5-preview-free
# ⚠️ โมเดลที่ถูกลบออกก่อนหน้า (ไม่มีใน opencode models แล้ว → "Model not found"):
#    muse-spark-1.3-contributor-free, space-bunny-free
# ⚠️ โมเดลที่มีอยู่แต่ใช้ไม่ได้จาก repo root:
#    beam-free (gateway ปฏิเสธ agents_md), glm-5.3-flash-free (unknown_parameter)
DEFAULT_MODEL = "opencode/deepseek-v4.1-flash-free"
# ยืนยันแล้วว่าใช้ได้จริงจาก repo root (2026-10-25) — ทดสอบทีละตัว
# ดูวิธีทดสอบ: python scripts/check-model-health.py --verify <model>
MODEL_FALLBACKS = [
    "opencode/deepseek-v4.1-flash-free",       # ตัวหลัก · 15.1s · steadier สุด
    "opencode/nemotron-3.5-lightning-free",    # 13.2s · ไทย 1087
    "opencode/nemotron-3-ultra-free",          # 19.0s · ไทย 702
    "opencode/big-pickle",                     # 19.8s · ไทย 871
    "opencode/mimo-v2.6-flash-free",           # 82.9s + ชอบเรียก tool · ท้ายสุด
]
# Dead models — ถ้ามี caller ส่งชื่อเก่ามา ให้ map เข้า fallback chain ทันที
DEAD_MODELS = {
    # ยังไม่มีใน opencode models (Model not found)
    "opencode/x-preview-f-free",
    "opencode/muse-spark-1.3-contributor-free",
    "opencode/space-bunny-free",
    "opencode/deepseek-v4-flash-free",
    "stealth/ox-alpha",
    # หาย upstream 2026-10-25 (Model unavailable) — เดิมอยู่ใน chain
    "opencode/minimax-m3.1-flash-free",
    "opencode/longcat-2.5-preview-free",
    # มีอยู่แต่ gateway free-tier ปฏิเสธ agents_md / unknown_parameter
    "opencode/beam-free",
    "opencode/glm-5.3-flash-free",
}

# ── Model health check (กันโมเดลตายเงียบ) ────────────────────────────
# โมเดลฟรีของ opencode ถูกเปลี่ยนชื่อ/ลบไปเรื่อย ๆ → chain นี้จะตาย
# โดยไม่มี error ชัดเจน (ทุกโมเดลคืน "empty response")
# → ต้องตรวจชื่อเป็นระยะ แล้วเตือนก่อนที่ agent ทั้ง 19 ตัวจะ "ตาบอด"

_MODEL_CACHE_PATH = Path(
    os.environ.get(
        "SOLOCORP_MODEL_HEALTH_CACHE",
        str(Path(__file__).parent.parent / "bus" / "system" / "model_health.json"),
    )
)
_MODEL_CACHE_TTL_HOURS = 6
_MODELS_TIMEOUT = 30


def list_available_models(prefix: str = "opencode/") -> list[str]:
    """รายชื่อโมเดลที่ opencode มีจริง ณ ตอนนี้ (เรียก CLI)

    Returns:
        list[str]: เช่น ["opencode/deepseek-v4.1-flash-free", ...]
        คืน [] ถ้าเรียกไม่ได้ (ไม่มี opencode / timeout)
    """
    import subprocess

    try:
        r = subprocess.run(
            [_CMD, "models"], capture_output=True, text=True,
            timeout=_MODELS_TIMEOUT,
        )
    except Exception:
        return []

    out = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if line.startswith(prefix):
            out.append(line)
    return out


def _read_model_cache() -> dict:
    try:
        if not _MODEL_CACHE_PATH.exists():
            return {}
        data = json.loads(_MODEL_CACHE_PATH.read_text(encoding="utf-8"))
        checked = data.get("checked_at")
        if not checked:
            return {}
        age_h = (datetime.now(timezone.utc)
                 - datetime.fromisoformat(checked)).total_seconds() / 3600
        if age_h > _MODEL_CACHE_TTL_HOURS:
            return {}
        return data
    except Exception:
        return {}


def _write_model_cache(models: list[str]) -> None:
    try:
        _MODEL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _MODEL_CACHE_PATH.write_text(json.dumps({
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "available": models,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def audit_models(use_cache: bool = True) -> dict:
    """เทียบ MODEL_FALLBACKS กับโมเดลที่มีจริง → รายงานสุขภาพ chain

    Returns:
        dict: {
            ok: bool,             # ไม่มีโมเดลใน chain หาย
            chain: [...],         # chain ปัจจุบัน
            available: [...],     # โมเดล opencode/ ที่มีจริง (ทั้งหมด)
            missing: [...],       # ใน chain แต่ไม่มีจริง  ← ต้องแก้
            usable: [...],        # ใน chain ที่มีจริง
            candidates: [...],    # มีจริงแต่ยังไม่อยู่ใน chain (ข้อเสนอ)
            checked_at: str,
            stale: bool,          # ใช้ข้อมูล cache
            error: str | None,
        }
    """
    cached = _read_model_cache() if use_cache else {}
    if cached.get("available"):
        available = list(cached["available"])
        stale = True
        checked_at = cached.get("checked_at", "")
    else:
        available = list_available_models()
        stale = False
        checked_at = datetime.now(timezone.utc).isoformat()
        if available:
            _write_model_cache(available)

    chain = list(MODEL_FALLBACKS)
    if not available:
        return {
            "ok": True, "chain": chain, "available": [], "missing": [],
            "usable": chain, "candidates": [], "checked_at": checked_at,
            "stale": stale, "error": "อ่านรายชื่อโมเดลไม่ได้ (ข้ามการตรวจ)",
        }

    avail_set = set(available)
    missing = [m for m in chain if m not in avail_set]
    usable = [m for m in chain if m in avail_set]
    candidates = [m for m in available if m not in chain]

    return {
        "ok": not missing,
        "chain": chain,
        "available": available,
        "missing": missing,
        "usable": usable,
        "candidates": candidates,
        "checked_at": checked_at,
        "stale": stale,
        "error": None,
    }
_CMD = os.environ.get("OPENCODE_BIN", os.path.expanduser("~/.opencode/bin/opencode"))
# agent สำหรับงาน LLM แบบ one-shot: ต้อง read-only/ไม่มี tool ที่ต้องขออนุญาต
# default agent ของโปรเจกต์ (ceo-hanuman) มี shell/write → subprocess ที่ไม่มี TTY
# จะค้างที่ "permission requested: shell" แล้วล้มทั้ง chain
_AGENT = os.environ.get("OPENCODE_AGENT", "plan")
_MAX_CONCURRENT = 3
_LLM_TIMEOUT = 60
_MAX_RETRIES = 3
_CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# จะได้ reuse context ทุกครั้ง (ไม่ต้อง search path ใหม่)
# --agent plan = built-in read-only agent (ไม่มี shell/edit → ไม่มี permission prompt)
# stdout ยังสะอาด: banner "> agent · model" ออกทาง stderr (ยืนยัน 2026-10-25, 3/3 รัน)
_CMD_WITH_FLAGS = [_CMD, "run", "--agent", _AGENT]

# Concurrency control
_semaphore = asyncio.Semaphore(_MAX_CONCURRENT)


# ── Provider Functions ─────────────────────────────────────────────────


async def think(
    prompt: str,
    system_prompt: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 500,
    temperature: float = 0.7,
    timeout: Optional[int] = None,
    agent: str = "",
) -> str:
    """ให้ LLM คิดและตอบกลับ — ใช้ได้จากทุก Agent

    Args:
        prompt: คำถาม/คำสั่งถึง LLM
        system_prompt: context/brief เพิ่มเติม (เช่น บทบาท agent)
        model: ชื่อ model (default: deepseek-v4.1-flash-free; ตัวอื่นดู MODEL_FALLBACKS)
        max_tokens: ความยาวสูงสุดของคำตอบ
        temperature: (reserved) ไม่ได้ส่งไป opencode run โดยตรง
        timeout: override timeout (วินาที) — prompt ยาว/ภาษาไทยต้องใช้เวลานาน
        agent: ชื่อ agent ที่เรียก (สำหรับ ledger — ใครกินโควตา)

    Returns:
        str: ข้อความตอบกลับจาก LLM (ตัด max_tokens แล้ว)

    หมายเหตุ: ค่าใช้จ่ายจริงของ call นี้ถูกบันทึกใน bus/system/token-ledger.jsonl
    ถ้าโควตาถูกล็อกอยู่ (429/402 ที่เจอมาแล้ว) ฟังก์ชันนี้คืนทันทีโดยไม่ยิง LLM
    """
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    last_error = ""

    # ── Pre-flight 1: โควตาถูกล็อกอยู่ไหม (ประหยัดเวลา + ไม่ยิงเข้ากำแพง) ──
    quota = token_ledger.quota_status()
    if quota["locked"]:
        mins = quota["remaining_s"] // 60
        log.error(
            f"LLM ข้าม: quota lock ถึง {quota['until']} (~{mins} นาที) — {quota['reason']}"
        )
        return (
            f"⚠️ LLM ไม่พร้อม: โควตาถูกล็อกถึง {quota['until']} "
            f"(~{mins} นาที, {quota['reason']}) — ไม่ยิงซ้ำเพื่อไม่ให้เสียเวลาเปล่า"
        )

    # ── Pre-flight 2: งบรายวัน (requests / output / cost) ──────────────────
    budget = token_ledger.check_budget()
    if not budget["ok"]:
        log.error(f"LLM ข้าม: เกินงบรายวัน — {budget['reason']}")
        return (
            f"⚠️ LLM ไม่พร้อม: เกินงบรายวัน ({budget['reason']}) — "
            "ปรับเพดานที่ SOLOCORP_LLM_DAILY_*"
        )
    if budget["warn"]:
        log.warning(
            f"LLM ใกล้งบรายวันแล้ว: {token_ledger.format_usage(budget['totals'])}"
        )

    # Build try-list: requested model first, then fallbacks (skip duplicates).
    # Dead models map straight to full chain.
    if model in DEAD_MODELS or model == DEFAULT_MODEL or model in MODEL_FALLBACKS:
        try_list = list(MODEL_FALLBACKS)
        # ถ้า caller เจาะจงตัวใน chain ให้เริ่มจากตัวนั้นก่อน
        if model in MODEL_FALLBACKS:
            try_list.remove(model)
            try_list.insert(0, model)
    else:
        try_list = [model] + [m for m in MODEL_FALLBACKS if m != model]

    for model_name in try_list:
        stop_chain = False
        for attempt in range(1, _MAX_RETRIES + 1):
            session_id = token_ledger.new_session_id()
            started = time.monotonic()
            try:
                async with _semaphore:
                    result = await _run_opencode(
                        full_prompt, model_name, timeout=timeout, session_id=session_id
                    )

                duration_ms = int((time.monotonic() - started) * 1000)
                usage = await token_ledger.read_session_usage_async(session_id)
                _record_call(
                    agent, model_name, session_id, usage, duration_ms,
                    ok=True, prompt_chars=len(full_prompt), result_chars=len(result),
                )

                if not result:
                    log.warning(f"LLM เปล่า ({model_name} attempt {attempt})")
                    last_error = f"{model_name}: empty response"
                    break  # เปล่า = เปลี่ยนโมเดลเลย ไม่ retry ตัวเดิมซ้ำ

                if model_name != try_list[0]:
                    log.info(f"LLM fallback สำเร็จด้วย {model_name}")
                return result[:max_tokens]

            except asyncio.TimeoutError:
                duration_ms = int((time.monotonic() - started) * 1000)
                usage = await token_ledger.read_session_usage_async(session_id)
                _record_call(
                    agent, model_name, session_id, usage, duration_ms,
                    ok=False, error=f"timeout ({timeout or _LLM_TIMEOUT}s)",
                    prompt_chars=len(full_prompt),
                )
                log.warning(f"LLM timeout {model_name} attempt {attempt}/{_MAX_RETRIES}")
                last_error = f"{model_name}: timeout ({timeout or _LLM_TIMEOUT}s)"
                continue

            except Exception as e:
                duration_ms = int((time.monotonic() - started) * 1000)
                usage = await token_ledger.read_session_usage_async(session_id)
                _record_call(
                    agent, model_name, session_id, usage, duration_ms,
                    ok=False, error=str(e), prompt_chars=len(full_prompt),
                )
                log.warning(f"LLM error {model_name} attempt {attempt}/{_MAX_RETRIES}: {e}")
                last_error = f"{model_name}: {e}"
                # Model not found / unavailable = ข้ามไปตัวถัดไปทันที ไม่ต้อง retry ซ้ำ
                # (v2.1.4 พูดว่า "Model unavailable" — เช็คทั้งสองคำแบบ case-insensitive)
                if _is_dead_model_error(str(e)):
                    break
                # โควตา/เงินตัน = ทุกโมเดลจะล้มเหมือนกัน (ADR-017)
                # ไม่ต้อง retry ทั้ง chain (5 โมเดล × 3 ครั้ง = เสียเวลาหลายนาทีเปล่า ๆ)
                # → ล็อกจนถึงเวลา reset แล้วบอก root cause ให้ชัด
                if token_ledger.is_quota_error(str(e)):
                    st = token_ledger.lock_from_error(str(e), model=model_name)
                    last_error = (
                        "free-tier/quota หมด: การเรียกผ่าน opencode run ถูกจำกัด (ADR-017) "
                        f"— ล็อกถึง {st['until']} (~{st['remaining_s'] // 60} นาที) "
                        "ไม่ยิงซ้ำจนถึงเวลานั้น"
                    )
                    log.error(
                        f"LLM quota lock → {st['until']} ({st['reason']}) — หยุด chain"
                    )
                    stop_chain = True
                    break
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(attempt)
                continue
        if stop_chain:
            break

    log.error(f"LLM หมดโอกาส (ลอง {len(try_list)} โมเดล): {last_error}")
    return f"⚠️ LLM ไม่พร้อม: {last_error}"


def _record_call(
    agent: str,
    model: str,
    session_id: str,
    usage: dict,
    duration_ms: int,
    *,
    ok: bool,
    error: str = "",
    prompt_chars: int = 0,
    result_chars: int = 0,
) -> None:
    """เขียน 1 บรรทัดลง ledger — ห้าม raise (accounting ต้องไม่ฆ่า LLM call)"""
    try:
        entry = {
            "agent": agent or os.environ.get("SOLOCORP_AGENT_NAME", "unknown"),
            "model": model,
            "session_id": session_id,
            "ok": ok,
            "duration_ms": duration_ms,
            "prompt_chars": prompt_chars,
            "result_chars": result_chars,
            "error": (error or "")[:300],
        }
        for key in ("requests", "input", "output", "reasoning",
                    "cache_read", "cache_write", "cost"):
            entry[key] = usage.get(key, 0)
        token_ledger.record(entry)

        if usage.get("error"):
            log.warning(f"อ่าน usage ไม่ได้ ({session_id}): {usage['error']}")
        elif ok:
            log.info(
                f"LLM {model} {duration_ms}ms {token_ledger.format_usage(usage)}"
            )
    except Exception as e:  # noqa: BLE001 — accounting ต้องไม่ทำให้ call ล้ม
        log.debug(f"บันทึก usage ไม่สำเร็จ: {e}")



def _is_dead_model_error(message: str) -> bool:
    """error ที่แปลว่า "โมเดลนี้ใช้ไม่ได้" → ข้ามทันที ไม่ต้อง retry ตัวเดิม 3 ครั้ง

    opencode v2.1.4 คืน `Model unavailable: <model>` (ไม่ใช่ "Model not found")
    → ถ้าเช็คแต่คำเดิม จะเสีย ~3s ต่อโมเดลตาย 1 ตัวในทุก think()
    """
    low = message.lower()
    return "model not found" in low or "model unavailable" in low


async def _run_opencode(
    full_prompt: str,
    model: str,
    *,
    timeout: Optional[int] = None,
    session_id: Optional[str] = None,
) -> str:
    """เรียก LLM ผ่าน opencode run CLI (core)

    spawn subprocess → ส่ง prompt ผ่าน stdin → อ่าน stdout
    ใช้ --agent (read-only) + --model เท่านั้น (ไม่ส่ง flag ที่ CLI ไม่รู้จัก — ดู _CMD_WITH_FLAGS)
    session_id: ถ้าระบุ จะส่ง `--session <id>` → สร้าง session ใหม่ด้วย id ของเรา
      (ไม่ได้เปลี่ยนพฤติกรรม: ปกติ opencode ก็สร้าง session ใหม่ทุก run)
      ประโยชน์: ตามรอย usage ใน opencode.db + console request logs ได้แบบ 1:1
    """
    cmd = [*_CMD_WITH_FLAGS, "--model", model]
    if session_id:
        cmd += ["--session", session_id]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=_CWD,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=full_prompt.encode("utf-8")),
            timeout=timeout or _LLM_TIMEOUT,
        )
    except asyncio.TimeoutError:
        _safe_kill(proc)
        raise

    exit_code = await _safe_wait(proc)
    result = stdout.decode("utf-8", errors="replace").strip()

    if exit_code and exit_code != 0:
        err = stderr.decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"opencode run exit {exit_code}: {err}")

    return result


def _safe_kill(proc: asyncio.subprocess.Process) -> None:
    """ฆ่า process + ป้องกัน ProcessLookupError"""
    try:
        proc.kill()
    except ProcessLookupError:
        pass
    except OSError:
        pass


async def _safe_wait(proc: asyncio.subprocess.Process) -> int:
    """รอเก็บ zombie + คืน returncode"""
    try:
        return await proc.wait()
    except ProcessLookupError:
        return proc.returncode or -1
    except OSError:
        return proc.returncode or -1


# ── Utility ────────────────────────────────────────────────────────────

def count_tokens(text: str) -> int:
    """นับจำนวน token โดยประมาณ (ไทย + อังกฤษ)"""
    import re
    thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
    eng_words = len(re.findall(r'[a-zA-Z]+', text))
    return thai_chars + eng_words + len(text.split())
