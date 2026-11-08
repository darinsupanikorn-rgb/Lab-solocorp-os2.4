"""App runtime — ประสาน registry, module host และ provider settings ในกระบวนการเดียว.

ออกแบบตาม design note D1 (single local process): รันคำสั่งเดียวแล้ว state
อยู่ใน memory เดียวกัน ไม่ต้องมี IPC ระหว่าง shell กับ API.

ทุกอย่างอ่าน/เขียนผ่าน registry + module host ที่มีอยู่แล้ว (CMD-006 ห้ามแต่ง
module_registry*.py) — รuntime นี้เป็นตัวเรียกใช้เท่านั้น.
"""

from __future__ import annotations

from typing import Any

from solocorp_mcp.module_host import ModuleHost
from solocorp_mcp.module_registry import ModuleRegistry
from solocorp_app.provider import ProviderSettings, load_provider_settings


class AppRuntime:
    """ตัวประสานหลักของแอป SoloCorp (เฟส 1: registry + provider + UI toggle)."""

    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        host: ModuleHost | None = None,
        provider: ProviderSettings | None = None,
    ) -> None:
        self.registry = registry or ModuleRegistry()
        self.host = host or ModuleHost(registry=self.registry)
        self.provider = provider or load_provider_settings()

    # ---------------------------------------------------------------- registry

    def status(self) -> dict[str, Any]:
        """มุมมองรวมของทุกโมดูล (config intent + รuntime observation)."""
        return self.registry.status()

    def toggle_module(self, module_id: str, status: str) -> dict[str, Any]:
        """เปิด/ปิดโมดูล — เขียนเฉพาะ tracked config, ไม่แตะไฟล์ state."""
        if status not in {"enabled", "disabled"}:
            raise ValueError("status ต้องเป็น 'enabled' หรือ 'disabled' เท่านั้น")
        return self.registry.update(module_id, status)

    # ---------------------------------------------------------------- modules

    def health_all(self) -> list[dict[str, Any]]:
        """เช็กสุขภาพทุกโมดูลที่เปิดอยู่ (ทนทาน — ผิดพลาดรายตัวไม่พังทั้งหมด)."""
        return self.host.health_all()

    # ---------------------------------------------------------------- provider

    def provider_status(self) -> dict[str, Any]:
        """คืนสรุป provider settings (ไม่รวมค่า credential จริง)."""
        return {
            "provider": self.provider.provider,
            "model": self.provider.model,
            "base_url": self.provider.base_url,
            "api_key_ref": self.provider.api_key_ref,
            "configured": self.provider.is_configured(),
        }

    def save_provider(self, settings: ProviderSettings) -> None:
        """ตั้งค่า provider ใหม่แล้วคงไว้ใน config/provider.json."""
        self.provider = settings
        from solocorp_app.provider import save_provider_settings

        save_provider_settings(settings)

    # ---------------------------------------------------------------- lifecycle

    def close(self) -> None:
        """ปิดกระบวนการโมดูลทั้งหมด (เรียกขณะปิดแอป)."""
        self.host.close_all()
