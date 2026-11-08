"""SoloCorp App — local-first runtime shell (Phase 1).

กระบวนการเดียว: FastAPI serve UI (Jinja, server-rendered, ไม่มี SPA framework)
บวก JSON API เล็ก ๆ ผูกกับ registry, module host และ provider settings.

ผูก loopback เท่านั้น (127.0.0.1), พอร์ตdefault 8766, override ผ่าน environment.

Phase 1 gate (PRD §11 / design note §6 แผนที่ 4):
  ผู้ใช้ตั้งค่าหนึ่ง model/provider ได้ และเปิด/ปิด Content Creator module
  จากหน้า UI ของแอปจริง.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from solocorp_mcp.module_registry import PERSISTENT_STATUSES
from solocorp_mcp.task_tracking import TaskTracker
from solocorp_app.provider import (
    ProviderSettings,
    ProviderSettingsError,
    load_provider_settings,
    save_provider_settings,
)
from solocorp_app.runtime import AppRuntime

APP_TITLE = "SoloCorp OS"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _render(
    request: Request,
    name: str,
    status_code: int = 200,
    **extra: Any,
) -> HTMLResponse:
    context: dict[str, Any] = {"request": request, "app_title": APP_TITLE, **extra}
    return TEMPLATES.TemplateResponse(request, name, context, status_code=status_code)


def _redirect(
    url: str, *, msg: str | None = None, kind: str = "info"
) -> RedirectResponse:
    if msg:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}msg={msg}&kind={kind}"
    return RedirectResponse(url, status_code=303)


def create_app(runtime: AppRuntime | None = None) -> FastAPI:
    """สร้าง FastApp application (รองรับ uvicorn --factory)."""
    runtime = runtime or AppRuntime()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: เช็กสุขภาพโมดูลที่เปิดอยู่ (ทนทาน — แอปต้องเริ่มได้แม้โมดูล
        # บางตัวสตาร์ทไม่ติด, เช่นยังไม่มี mcp package หรือ credentials)
        try:
            runtime.health_all()
        except Exception:  # noqa: BLE001 — startup ต้องไม่ตายเพราะ probe โมดูล
            pass
        yield
        runtime.close()

    app = FastAPI(title=APP_TITLE, lifespan=lifespan)

    # Static assets (CSS)
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )

    # ------------------------------------------------------------------ pages

    @app.get("/", response_class=HTMLResponse)
    @app.get("/modules", response_class=HTMLResponse)
    async def modules_page(request: Request):
        status = runtime.status()
        return _render(
            request,
            "modules.html",
            modules=status["modules"],
            summary=status,
            msg=request.query_params.get("msg"),
            kind=request.query_params.get("kind", "info"),
        )

    @app.post("/modules/{module_id}/toggle")
    async def toggle_module(module_id: str, status: str = Form(...)):
        """เปิด/ปิดโมดูลจาก UI — เขียนลง config/module-registry.json จริง."""
        if status not in PERSISTENT_STATUSES:
            return _redirect(
                "/modules",
                msg=f"สถานะไม่ถูกต้อง: {status}",
                kind="error",
            )
        try:
            runtime.toggle_module(module_id, status)
        except ValueError as exc:
            return _redirect("/modules", msg=str(exc), kind="error")
        label = "เปิด" if status == "enabled" else "ปิด"
        return _redirect("/modules", msg=f"{module_id}: {label} แล้ว", kind="info")

    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page(request: Request):
        provider = load_provider_settings()
        return _render(
            request,
            "settings.html",
            provider=provider,
            configured=provider.is_configured(),
            msg=request.query_params.get("msg"),
            kind=request.query_params.get("kind", "info"),
        )

    @app.post("/settings")
    async def save_settings(
        request: Request,
        provider: str = Form(...),
        model: str = Form(...),
        base_url: str = Form(""),
        api_key_ref: str = Form(""),
    ):
        try:
            settings = ProviderSettings(
                provider=provider.strip(),
                model=model.strip(),
                base_url=base_url.strip() or None,
                api_key_ref=api_key_ref.strip(),
            )
            if not settings.provider or not settings.model or not settings.api_key_ref:
                raise ProviderSettingsError(
                    "provider, model และ api_key_ref ต้องไม่เว้นว่าง"
                )
            save_provider_settings(settings)
        except ProviderSettingsError as exc:
            return _redirect("/settings", msg=str(exc), kind="error")
        return _redirect("/settings", msg="บันทึกการตั้งค่า provider แล้ว", kind="info")

    @app.get("/tasks", response_class=HTMLResponse)
    async def tasks_page(request: Request):
        tracker = TaskTracker()
        tasks = tracker.list_tasks()
        return _render(
            request,
            "tasks.html",
            tasks=tasks,
            msg=request.query_params.get("msg"),
            kind=request.query_params.get("kind", "info"),
        )

    @app.get("/ceo", response_class=HTMLResponse)
    async def ceo_page(request: Request):
        return _render(
            request,
            "ceo.html",
            configured=load_provider_settings().is_configured(),
            content_enabled=runtime.status()["modules"].get("content-creator", {}).get(
                "status"
            )
            == "enabled",
            msg=request.query_params.get("msg"),
            kind=request.query_params.get("kind", "info"),
        )

    # ------------------------------------------------------------------ API (JSON)

    @app.get("/api/registry")
    async def api_registry() -> dict[str, Any]:
        return runtime.status()

    @app.get("/api/provider")
    async def api_provider() -> dict[str, Any]:
        settings = load_provider_settings()
        return {
            "provider": settings.provider,
            "model": settings.model,
            "base_url": settings.base_url,
            "api_key_ref": settings.api_key_ref,
            "configured": settings.is_configured(),
            # ค่า credential จริงตั้งใจไม่ส่งกลับ — อ่านจาก env เท่านั้น
        }

    @app.post("/api/provider")
    async def api_save_provider(request: Request):
        try:
            data = await request.json()
        except Exception:  # noqa: BLE001
            return {"error": "invalid json"}, 400
        try:
            settings = ProviderSettings(
                provider=str(data.get("provider", "")).strip(),
                model=str(data.get("model", "")).strip(),
                base_url=data.get("base_url") or None,
                api_key_ref=str(data.get("api_key_ref", "")).strip(),
            )
            if not settings.provider or not settings.model or not settings.api_key_ref:
                raise ProviderSettingsError(
                    "provider, model และ api_key_ref ต้องไม่เว้นว่าง"
                )
            save_provider_settings(settings)
        except ProviderSettingsError as exc:
            return {"error": str(exc)}, 400
        return {"status": "saved", "provider": settings.provider}

    @app.get("/api/tasks")
    async def api_tasks() -> dict[str, Any]:
        tracker = TaskTracker()
        return {"tasks": tracker.list_tasks()}

    @app.get("/api/health")
    async def api_health() -> dict[str, Any]:
        registry_status = runtime.status()
        return {
            "host": DEFAULT_HOST,
            "port": DEFAULT_PORT,
            "registry_valid": registry_status["valid"],
            "content_module": registry_status["modules"].get("content-creator", {}),
        }

    return app


def main() -> None:
    """รันแอปตรง ๆ (เช่น `python -m solocorp_app.app`)."""
    import uvicorn

    uvicorn.run(
        create_app,
        host=os.environ.get("SOLOCORP_APP_HOST", DEFAULT_HOST),
        port=int(os.environ.get("SOLOCORP_APP_PORT", str(DEFAULT_PORT))),
        factory=True,
    )


if __name__ == "__main__":
    main()
