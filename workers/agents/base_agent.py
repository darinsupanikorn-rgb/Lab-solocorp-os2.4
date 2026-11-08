"""Base Agent — ทุก Agent ใน SoloCorp OS สืบทอดจากนี้"""

from __future__ import annotations

import json
import logging
import os
import asyncio
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)


class BaseAgent:
    """Base class สำหรับ Agent Workers ทั้งหมด

    แต่ละ Agent มี:
    - identity: SOUL.md profile
    - role: บทบาท หน้าที่ ขอบเขต
    - tools: เครื่องมือที่ใช้ทำงาน
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        profile_path: str | Path,
        bus_url: str = "http://127.0.0.1:8099",
        api_key: str = "",
    ):
        self.agent_id = agent_id
        self.name = name
        self.profile_path = Path(profile_path)
        self.bus_url = bus_url.rstrip("/")
        self.api_key = api_key or os.environ.get(
            "SOLOCORP_API_KEY", "sk-solocorp-admin-local-dev-001"
        )
        self.soul: dict[str, Any] = {}
        self._load_profile()

    def _load_profile(self) -> None:
        """โหลด SOUL.md — รู้จักตัวเอง"""
        if self.profile_path.exists():
            content = self.profile_path.read_text(encoding="utf-8")
            self.soul = {"raw": content, "lines": content.splitlines()}
            log.info(f"✅ {self.agent_id} โหลด SOUL.md แล้ว")
        else:
            log.warning(f"⚠️ {self.agent_id} ไม่พบ SOUL.md ที่ {self.profile_path}")
            self.soul = {"raw": "", "lines": []}

    def get_identity_summary(self) -> str:
        """สรุป identity สั้นๆ สำหรับ report"""
        lines = self.soul.get("lines", [])
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return self.name

    # ── LLM — ให้ Agent คิดเองได้ ────────────────────────────────────────

    async def think(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """ให้ LLM คิดและตอบกลับ ตามบทบาท (role) ของ Agent นี้

        Args:
            prompt: คำถาม/คำสั่งให้ LLM คิด
            max_tokens: ความยาวสูงสุดของคำตอบ
            temperature: 0.0 = ตายตัว, 1.0 = สร้างสรรค์

        Returns:
            str: คำตอบจาก LLM
        """
        from workers.llm_provider import think as llm_think

        # สร้าง system prompt แบบกระชับจาก SOUL.md (ไม่เอาทั้งหมด)
        soul_lines = self.soul.get("lines", [])
        # ดึงเฉพาะบรรทัดสำคัญ: name, role, description, keywords
        key_lines = []
        for line in soul_lines[:60]:  # แค่ 60 บรรทัดแรก
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                key_lines.append(stripped)
        soul_summary = "\n".join(key_lines[:20])  # สรุปสั้นๆ

        system_prompt = (
            f"คุณคือ {self.name} (ID: {self.agent_id}) "
            f"ใน SoloCorp OS\n\n"
            f"--- บทบาทย่อ ---\n{soul_summary}\n\n"
            f"--- กฎ ---\n"
            f"- ตอบเป็นภาษาไทย ยกเว้นคำศัพท์เทคนิค\n"
            f"- กระชับ ได้ใจความ ภายใน 2-3 ย่อหน้า\n"
            f"- ถ้าไม่รู้หรือไม่แน่ใจ ให้บอกตรงๆ\n"
            f"- ใช้ข้อมูลจาก context ที่มี ไม่มโน\n"
            f"- ทำงานให้เสร็จในคำตอบเดียว — ห้ามตอบว่า 'จะเริ่ม' หรือ 'กำลังจะทำ'\n"
            f"  ให้ส่งผลลัพธ์จริง (ตัวเลข รายการ ข้อสรุป) กลับมาเลย\n"
            f"- อย่าใช้ markdown หรือ emoji เกินจำเป็น"
        )

        return await llm_think(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            agent=self.agent_id,
        )

    # ── Tools — เครื่องมือที่ Agent ใช้ ──────────────────────────────────

    async def read_file(self, path: str) -> str:
        """อ่านไฟล์"""
        p = Path(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        return f"❌ ไม่พบไฟล์: {path}"

    async def write_file(self, path: str, content: str) -> str:
        """เขียนไฟล์"""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"✅ เขียน {path} แล้ว ({len(content)} chars)"

    async def list_dir(self, path: str = ".") -> str:
        """รายการไฟล์ใน directory"""
        p = Path(path)
        if not p.exists():
            return f"❌ ไม่พบ: {path}"
        items = []
        for f in p.iterdir():
            suffix = "/" if f.is_dir() else ""
            items.append(f"  {f.name}{suffix}")
        return "\n".join(items[:50]) if items else "(empty)"

    async def run_command(self, cmd: str) -> str:
        """รัน shell command (limited)"""
        import subprocess
        try:
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            out = r.stdout.strip()[:2000]
            err = r.stderr.strip()[:500]
            result = out
            if err:
                result += f"\n⚠️ stderr: {err}"
            return result or "(no output)"
        except Exception as e:
            return f"❌ Command error: {e}"

    # ── Web — อ่านเว็บที่ต้อง render JavaScript ─────────────────────────

    async def web_read(self, url: str, wait: int = 12) -> str:
        """อ่านเนื้อหาเว็บ (render JS ได้ ไม่ต้องมี display)

        ใช้เมื่อ HTTP ธรรมดาดึงได้แค่ source code (React/Vue SPA, client-side only)

        Args:
            url: URL ที่ต้องการอ่าน
            wait: วินาทีที่รอให้หน้าโหลด (เว็บหนักใช้ 20-30)

        Returns:
            str: เนื้อหาเว็บ ห่อด้วย marker กัน prompt injection
        """
        from solocorp_skills.web import WebError, read_url, wrap_untrusted

        try:
            result = await asyncio.to_thread(read_url, url, wait=wait)
        except WebError as e:
            return f"❌ อ่านเว็บไม่สำเร็จ: {e}"
        except Exception as e:
            return f"❌ Web read error: {e}"

        header = f"# {result['title']}\n" if result["title"] else ""
        return header + wrap_untrusted(result["text"], result["url"])

    async def web_search(self, query: str, limit: int = 10) -> str:
        """ค้นหาข่าว/ข้อมูลบนเว็บ (รองรับภาษาไทย)

        Args:
            query: คำค้น
            limit: จำนวนผลลัพธ์สูงสุด

        Returns:
            str: รายการผลลัพธ์ (ชื่อเรื่อง + URL + snippet)
        """
        from solocorp_skills.web import WebError, search

        try:
            result = await asyncio.to_thread(search, query, limit=limit)
        except WebError as e:
            return f"❌ ค้นหาไม่สำเร็จ: {e}"
        except Exception as e:
            return f"❌ Search error: {e}"

        if not result["results"]:
            return f"ไม่พบผลลัพธ์สำหรับ '{query}'"

        lines = [f"# ผลการค้นหา: {query}", ""]
        for i, r in enumerate(result["results"], 1):
            lines.append(f"## {i}. {r['title']}")
            lines.append(f"URL: {r['url']}")
            lines.append(r["snippet"])
            lines.append("")
        return "\n".join(lines)

    # ── Report Back ─────────────────────────────────────────────────────

    async def report_to_ceo(
        self,
        task_id: str,
        status: str,
        summary: str,
        details: Optional[dict] = None,
    ) -> dict:
        """รายงานผลกลับไป CEO ผ่าน Central Bus"""
        import urllib.request

        payload = {
            "task_id": task_id,
            "source_agent": self.agent_id,
            "target_agent": "ceo-hanuman",
            "priority": "high" if status == "failed" else "normal",
            "payload": {
                "action": "report_back",
                "status": status,
                "summary": summary,
                "details": details or {},
                "agent": self.agent_id,
            },
        }
        req = urllib.request.Request(
            f"{self.bus_url}/v1/observe",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
            method="POST",
        )
        try:
            resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
            log.info(f"📤 {self.agent_id} รายงานไป CEO: {status} — {summary[:50]}")
            return resp
        except Exception as e:
            log.error(f"❌ {self.agent_id} รายงาน CEO ล้มเหลว: {e}")
            return {"status": "error", "error": str(e)}

    # ── Main execution — แต่ละ Agent Override ─────────────────────────

    async def execute(self, task: dict) -> dict:
        """Execute task — Override ใน subclass"""
        raise NotImplementedError("Subclass must implement execute()")

    def __str__(self) -> str:
        return f"{self.agent_id} ({self.name})"
