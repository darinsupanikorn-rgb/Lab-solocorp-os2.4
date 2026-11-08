"""Provider settings adapter for the SoloCorp App (PRD D5 / design note §5.5).

การออกแบบสำคัญ (คัดลอกจาก design note):

* ที่เก็บตั้งค่า: ``config/provider.json`` (tracked ใน git เมื่อไม่มีความลับ)
* credential จริงอยู่ใน environment variable อ้างถึงด้วยชื่อผ่าน ``api_key_ref``
  — **ไม่เขียนค่าจริงลงไฟล์ config**, ไม่รั่วเข้าที่ task artifact
* **ไม่มี silent fallback:** provider หรือ model ไม่ใช้งาน = รายงานเป็น error ชัดเจน
  ห้ามเด้งโมเดลอื่นโดยไม่แจ้งผู้ใช้
* adapter オブジェกต์นี้คือส่วนเดียวที่ CEO loop เรียก; content MCP ที่เรียก
  provider เอง (เช่น ElevenLabs) คงอยู่ฝั่ง module ไม่ปนกัน

ไฟล์นี้เป็นชั้นโค้ด (code layer) เท่านั้น — ไม่เกี่ยวกับการตัดสินใจ
permissions enum ของ CMD-006 ซึ่งอยู่ในอำนาจสถาปนิก เคาะแล้วจึง implement แยกต่างหาก
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "provider.json"


class ProviderSettingsError(ValueError):
    """การตั้งค่า provider ไม่ถูกต้อง หรือยังไม่ครบถ้วน."""


@dataclass
class ProviderSettings:
    provider: str = ""
    model: str = ""
    base_url: str | None = None
    api_key_ref: str = ""

    def is_configured(self) -> bool:
        """ยังไม่เรียก provider จริง — แค่ตรวจว่ามี metadata ครบหรือไม่."""
        return bool(self.provider and self.model and self.api_key_ref)

    def api_key(self) -> str | None:
        """คืน credential จริงจาก environment variable ตามชื่อใน api_key_ref.

        คืน None ถ้ายังไม่ตั้งค่า ref. ค่าที่คืนมา **ไม่เคยถูกเก็บในไฟล์ใดของระบบ**.
        """
        if not self.api_key_ref:
            return None
        return os.environ.get(self.api_key_ref)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_provider_settings(path: Path = CONFIG_PATH) -> ProviderSettings:
    """อ่าน provider settings จากไฟล์ config.

    ไฟล์ไม่มี (รันครั้งแรก) = คืนค่า object ว่าง (unconfigured), **ไม่ raise**.
    """
    if not path.exists():
        return ProviderSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ProviderSettingsError(f"{path} อ่านไม่ได้หรือไม่ใช่ JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ProviderSettingsError(f"{path} root ต้องเป็น object")
    return ProviderSettings(
        provider=str(data.get("provider", "") or ""),
        model=str(data.get("model", "") or ""),
        base_url=data.get("base_url"),
        api_key_ref=str(data.get("api_key_ref", "") or ""),
    )


def save_provider_settings(
    settings: ProviderSettings, path: Path = CONFIG_PATH
) -> None:
    """เขียน provider settings ลง ``config/provider.json``.

    เก็บเฉพาะ metadata (ไม่รวมค่า credential จริง) — credential ปล่อยไว้ใน env var
    ที่ชื่อตรงกับ api_key_ref.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
