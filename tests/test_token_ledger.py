"""เทสต์ token/quota accounting — ไม่ใช้ LLM, ไม่ใช้เน็ต

บริบท (2026-10-25): โควตาฟรีหมดกลางวันโดยไม่มีใครรู้ — 297 requests สำเร็จ
แล้วอีก 186 requests ถูกยิงเข้ากำแพง 429 เปล่า ๆ เพราะไม่มีตัววัดและไม่มีความจำ
เทสต์ชุดนี้ล็อกพฤติกรรม 3 อย่าง:
  1. อ่าน usage จริงจาก opencode.db ได้ (schema เดียวกับของจริง)
  2. ledger + เพดานรายวันทำงาน และ **ไม่ล้ม** เมื่อไฟล์/DB มีปัญหา
  3. quota lock จำเวลา reset แล้วทำให้ call ถัดไป fail fast
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workers import token_ledger as tl  # noqa: E402


# ══════════════════════════════════════════════════════════════════════
# Fixtures — DB ปลอมที่มี schema เหมือนของจริง
# ══════════════════════════════════════════════════════════════════════


def _make_db(path: Path, rows: list[tuple[str, str, str]]) -> Path:
    """สร้าง session_message แบบเดียวกับ opencode.db จริง

    rows: [(session_id, type, data_json), ...]
    """
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE session_message (
               id text PRIMARY KEY, session_id text NOT NULL, type text NOT NULL,
               seq integer, time_created integer NOT NULL, time_updated integer NOT NULL,
               data text NOT NULL)"""
    )
    for i, (sid, typ, data) in enumerate(rows):
        conn.execute(
            "INSERT INTO session_message (id, session_id, type, seq, time_created, "
            "time_updated, data) VALUES (?,?,?,?,?,?,?)",
            (f"m{i}", sid, typ, i, 1_700_000_000_000 + i, 1_700_000_000_000 + i, data),
        )
    conn.commit()
    conn.close()
    return path


def _assistant(inp=0, out=0, reasoning=0, cache_read=0, cache_write=0, cost=0):
    return json.dumps({
        "time": {"created": 1, "completed": 2},
        "agent": "ceo-hanuman",
        "model": {"id": "deepseek-v4.1-flash-free", "providerID": "opencode"},
        "cost": cost,
        "tokens": {
            "input": inp, "output": out, "reasoning": reasoning,
            "cache": {"read": cache_read, "write": cache_write},
        },
    })


@pytest.fixture()
def tmp_db(tmp_path) -> Path:
    return _make_db(tmp_path / "opencode.db", [
        ("ses_llm_a", "assistant", _assistant(140, 471, 814, 60784, 0)),
        ("ses_llm_a", "assistant", _assistant(100, 200, 0, 1000, 0)),
        ("ses_llm_a", "user", json.dumps({"text": "hi"})),
        ("ses_llm_b", "assistant", _assistant(0, 0, 0, 0, 0)),  # request ที่ล้ม
    ])


# ══════════════════════════════════════════════════════════════════════
# 1. read_session_usage
# ══════════════════════════════════════════════════════════════════════


class TestReadSessionUsage:
    def test_sums_all_assistant_messages(self, tmp_db):
        u = tl.read_session_usage("ses_llm_a", db_path=tmp_db)
        assert u["requests"] == 2
        assert u["input"] == 240
        assert u["output"] == 671
        assert u["reasoning"] == 814
        assert u["cache_read"] == 61784
        assert u["error"] == ""

    def test_ignores_non_assistant_rows(self, tmp_db):
        u = tl.read_session_usage("ses_llm_a", db_path=tmp_db)
        assert u["requests"] == 2  # ไม่นับ user message

    def test_failed_request_counted_separately(self, tmp_db):
        """แถวที่ไม่มี token เลย = request ที่ล้ม (429) → failed ไม่ใช่ requests"""
        u = tl.read_session_usage("ses_llm_b", db_path=tmp_db)
        assert u["requests"] == 0
        assert u["failed"] == 1

    def test_unknown_session_is_zero_not_crash(self, tmp_db):
        u = tl.read_session_usage("ses_llm_nope", db_path=tmp_db, retries=1)
        assert u["requests"] == 0
        assert u["input"] == 0

    def test_missing_db_returns_zero_with_error(self, tmp_path):
        u = tl.read_session_usage("ses_x", db_path=tmp_path / "nope.db")
        assert u["requests"] == 0
        assert "ไม่พบ" in u["error"]

    def test_missing_table_returns_zero_with_error(self, tmp_path):
        p = tmp_path / "empty.db"
        sqlite3.connect(p).close()
        u = tl.read_session_usage("ses_x", db_path=p, retries=1)
        assert u["requests"] == 0
        assert "sqlite" in u["error"]

    def test_corrupt_json_row_skipped(self, tmp_path):
        p = _make_db(tmp_path / "db.db", [
            ("ses_llm_c", "assistant", "{not json"),
            ("ses_llm_c", "assistant", _assistant(10, 5, 0, 0, 0)),
        ])
        u = tl.read_session_usage("ses_llm_c", db_path=p)
        assert u["requests"] == 1
        assert u["input"] == 10

    def test_cost_summed(self, tmp_path):
        p = _make_db(tmp_path / "db.db", [
            ("s", "assistant", _assistant(1000, 1000, 0, 0, 0, cost=0.25)),
            ("s", "assistant", _assistant(1000, 1000, 0, 0, 0, cost=0.75)),
        ])
        assert tl.read_session_usage("s", db_path=p)["cost"] == pytest.approx(1.0)

    def test_async_wrapper(self, tmp_db):
        import asyncio
        u = asyncio.run(tl.read_session_usage_async("ses_llm_a", db_path=tmp_db))
        assert u["requests"] == 2


# ══════════════════════════════════════════════════════════════════════
# 2. ledger + today_totals
# ══════════════════════════════════════════════════════════════════════


class TestLedger:
    def test_record_then_today_totals(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        assert tl.record({"requests": 1, "input": 100, "output": 50, "cost": 0.01}, path=led)
        assert tl.record({"requests": 1, "input": 200, "output": 70, "cost": 0.02}, path=led)

        t = tl.today_totals(path=led)
        assert t["requests"] == 2
        assert t["input"] == 300
        assert t["output"] == 120
        assert t["cost"] == pytest.approx(0.03)

    def test_failed_entries_do_not_consume_budget(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        tl.record({"requests": 1, "output": 10, "ok": True}, path=led)
        tl.record({"requests": 0, "output": 0, "ok": False, "error": "429"}, path=led)
        assert tl.today_totals(path=led)["requests"] == 1

    def test_other_days_excluded(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        tl.record({"requests": 5, "output": 999, "ts": "2020-01-01T00:00:00+07:00"}, path=led)
        tl.record({"requests": 1, "output": 10}, path=led)
        assert tl.today_totals(path=led)["requests"] == 1

    def test_corrupt_line_skipped(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        tl.record({"requests": 1, "output": 5}, path=led)
        with led.open("a", encoding="utf-8") as fh:
            fh.write("not-json\n")
        t = tl.today_totals(path=led)
        assert t["requests"] == 1
        assert t["corrupt"] == 1

    def test_undated_entry_reported_not_silently_counted(self, tmp_path):
        """บรรทัดที่ไม่มี ts ต้องไม่ถูกนับเป็นของวันนี้ (จะถูกนับซ้ำทุกวัน) แต่ต้องเห็นได้"""
        led = tmp_path / "ledger.jsonl"
        led.write_text('{"requests": 9, "output": 9}\n', encoding="utf-8")
        t = tl.today_totals(path=led)
        assert t["requests"] == 0
        assert t["undated"] == 1

    def test_missing_ledger_is_zero(self, tmp_path):
        t = tl.today_totals(path=tmp_path / "none.jsonl")
        assert t["requests"] == 0 and t["error"] == ""

    def test_unwritable_path_returns_false_not_raise(self, tmp_path):
        """ledger เขียนไม่ได้ = เตือนแล้วไปต่อ ห้ามทำให้ LLM call ล้ม"""
        target = tmp_path / "file.txt"
        target.write_text("x", encoding="utf-8")
        assert tl.record({"requests": 1}, path=target / "sub" / "ledger.jsonl") is False

    def test_record_fills_ts(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        tl.record({"requests": 1}, path=led)
        row = json.loads(led.read_text(encoding="utf-8").splitlines()[0])
        assert row["ts"][:2] == "20" and len(row["ts"]) >= 19


# ══════════════════════════════════════════════════════════════════════
# 3. budget
# ══════════════════════════════════════════════════════════════════════


class TestBudget:
    def test_under_limit_ok(self):
        r = tl.check_budget({"requests": 5, "output": 100, "cost": 0.0},
                            {"requests": 400, "warn_requests": 200,
                             "output_tokens": 1000, "cost_usd": 1.0})
        assert r["ok"] and not r["warn"]

    def test_requests_ceiling_blocks(self):
        r = tl.check_budget({"requests": 400, "output": 0, "cost": 0.0},
                            {"requests": 400, "warn_requests": 200,
                             "output_tokens": 10**9, "cost_usd": 100})
        assert not r["ok"] and "requests" in r["reason"]

    def test_output_ceiling_blocks(self):
        r = tl.check_budget({"requests": 1, "output": 2000, "cost": 0.0},
                            {"requests": 400, "warn_requests": 200,
                             "output_tokens": 2000, "cost_usd": 100})
        assert not r["ok"] and "output" in r["reason"]

    def test_cost_ceiling_blocks(self):
        r = tl.check_budget({"requests": 1, "output": 0, "cost": 1.5},
                            {"requests": 400, "warn_requests": 200,
                             "output_tokens": 10**9, "cost_usd": 1.0})
        assert not r["ok"] and "cost" in r["reason"]

    def test_warn_before_blocking(self):
        r = tl.check_budget({"requests": 250, "output": 0, "cost": 0.0},
                            {"requests": 400, "warn_requests": 200,
                             "output_tokens": 10**9, "cost_usd": 100})
        assert r["ok"] and r["warn"]

    def test_defaults_are_grounded(self):
        lim = tl.budget_limits()
        assert lim["requests"] == tl.DEFAULT_LIMITS["requests"]
        assert lim["warn_requests"] < lim["requests"]

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("SOLOCORP_LLM_DAILY_REQUESTS", "7")
        monkeypatch.setenv("SOLOCORP_LLM_DAILY_COST_USD", "0.5")
        lim = tl.budget_limits()
        assert lim["requests"] == 7 and lim["cost_usd"] == 0.5

    def test_invalid_env_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("SOLOCORP_LLM_DAILY_REQUESTS", "not-a-number")
        assert tl.budget_limits()["requests"] == tl.DEFAULT_LIMITS["requests"]


# ══════════════════════════════════════════════════════════════════════
# 4. quota lock
# ══════════════════════════════════════════════════════════════════════


class TestQuotaLock:
    def test_no_file_is_unlocked(self, tmp_path):
        assert tl.quota_status(path=tmp_path / "none.json")["locked"] is False

    def test_lock_then_status(self, tmp_path):
        p = tmp_path / "quota.json"
        until = int(time.time() * 1000) + 600_000
        assert tl.lock_quota(until, "free-limit", model="opencode/x", path=p) is True
        st = tl.quota_status(path=p)
        assert st["locked"] and 590 <= st["remaining_s"] <= 600
        assert st["reason"] == "free-limit" and st["model"] == "opencode/x"

    def test_expired_lock_is_unlocked(self, tmp_path):
        p = tmp_path / "quota.json"
        tl.lock_quota(int(time.time() * 1000) - 1000, "free-limit", path=p)
        assert tl.quota_status(path=p)["locked"] is False

    def test_clear_quota(self, tmp_path):
        p = tmp_path / "quota.json"
        tl.lock_quota(int(time.time() * 1000) + 600_000, "free-limit", path=p)
        assert tl.clear_quota(path=p) is True
        assert tl.quota_status(path=p)["locked"] is False

    def test_corrupt_file_is_unlocked(self, tmp_path):
        p = tmp_path / "quota.json"
        p.write_text("{{{", encoding="utf-8")
        assert tl.quota_status(path=p)["locked"] is False


class TestErrorParsing:
    # payload จริงจาก opencode v2.1.4 (2026-10-25)
    REAL_429 = (
        '{"type":"error","error":{"type":"provider.free-limit","message":"Free usage '
        'limit reached.","status":429,"response":{"body":"{\\"type\\":\\"error\\",'
        '\\"error\\":{\\"type\\":\\"FreeUsageLimitError\\"}}"}},"retryAfterMs":63736000}'
    )

    def test_parse_retry_after_ms(self):
        assert tl.parse_retry_after_ms(self.REAL_429) == 63_736_000

    def test_parse_retry_after_header_seconds(self):
        assert tl.parse_retry_after_ms("HTTP 429 Retry-After: 3600") == 3_600_000

    def test_parse_none(self):
        assert tl.parse_retry_after_ms("boom") is None

    def test_is_quota_error(self):
        assert tl.is_quota_error("FreeUsageLimitError: free usage limit reached")
        assert tl.is_quota_error("opencode run exit 1: free-tier gate")
        assert not tl.is_quota_error("Model unavailable: x")
        assert not tl.is_quota_error("boom")

    def test_is_funds_error(self):
        assert tl.is_funds_error("Upstream request failed: Insufficient account funds")
        assert not tl.is_funds_error("Model unavailable: x")

    def test_lock_from_error_uses_retry_after(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tl, "QUOTA_PATH", tmp_path / "quota.json")
        st = tl.lock_from_error(self.REAL_429, model="opencode/deepseek")
        assert st["locked"] is True
        # ~17.7 ชม.
        assert 63_000 <= st["remaining_s"] <= 63_800

    def test_lock_from_error_funds_reason(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tl, "QUOTA_PATH", tmp_path / "quota.json")
        st = tl.lock_from_error("Insufficient account funds", model="m")
        assert st["reason"] == "funds"
        assert 3500 <= st["remaining_s"] <= 3600  # default 1 ชม.

    def test_lock_from_error_unknown_uses_default(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tl, "QUOTA_PATH", tmp_path / "quota.json")
        st = tl.lock_from_error("weird", default_s=60)
        assert 55 <= st["remaining_s"] <= 60


# ══════════════════════════════════════════════════════════════════════
# 5. helpers
# ══════════════════════════════════════════════════════════════════════


class TestHelpers:
    def test_session_id_prefix_and_uniqueness(self):
        ids = {tl.new_session_id() for _ in range(50)}
        assert len(ids) == 50
        assert all(i.startswith("ses_llm") for i in ids)

    def test_format_usage_compact(self):
        s = tl.format_usage({"requests": 3, "input": 1200, "output": 500,
                             "reasoning": 0, "cache_read": 61_000, "cost": 0.0123})
        assert "req=3" in s and "1.2k" in s and "61.0k" in s and "$0.0123" in s


class TestTodayAttempts:
    def test_counts_ok_and_failed_separately(self, tmp_path):
        led = tmp_path / "ledger.jsonl"
        tl.record({"requests": 1, "ok": True}, path=led)
        tl.record({"requests": 0, "ok": False, "error": "429"}, path=led)
        tl.record({"requests": 0, "ok": False, "error": "429"}, path=led)
        c = tl.today_attempts(path=led)
        assert c["ok"] == 1 and c["failed"] == 2

    def test_missing_file(self, tmp_path):
        assert tl.today_attempts(path=tmp_path / "x.jsonl") == {
            "ok": 0, "failed": 0, "corrupt": 0
        }
