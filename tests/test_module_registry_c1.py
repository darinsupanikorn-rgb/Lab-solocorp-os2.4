"""C1 core contract tests: register/patch/atomic/tolerant-read.

These tests were written before the implementation (red-first). They pin the
registry-layer behaviours: register, patch-only update, orphan-state
tolerance and pruning, non-raising status, strict validate, atomic writes and
blocklist projection. Tool-surface and ModuleHost pins live in
``test_module_registry_tools.py`` and ``test_module_host.py``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from solocorp_mcp import module_registry
from solocorp_mcp.module_registry import ModuleRegistry
from solocorp_mcp.module_registry_schema import RegistrySchemaError


@pytest.fixture()
def registry(tmp_path: Path) -> ModuleRegistry:
    return ModuleRegistry(
        registry_path=tmp_path / "config" / "module-registry.json",
        state_path=tmp_path / "state" / "module-registry.state.json",
    )


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _state_entry(status: str = "connected") -> dict[str, Any]:
    return {
        "status": status,
        "last_checked": "2026-11-06T00:00:00+00:00",
        "response_time_ms": 1.5,
        "last_error": None,
    }


def _complete_entry(command: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": "enabled",
        "transport": "stdio",
        "command": command or ["/bin/echo", "hello"],
        "description": "stub module",
    }


# ── A1: register ─────────────────────────────────────────────────────


def test_register_adds_module_and_status_sees_it(registry: ModuleRegistry) -> None:
    result = registry.register("ghost", _complete_entry())

    assert result["status"] == "enabled"
    assert result["command"] == ["/bin/echo", "hello"]
    status = registry.status()
    assert status["modules"]["ghost"]["status"] == "enabled"
    assert status["modules"]["ghost"]["transport"] == "stdio"
    assert status["count"] == 6

    on_disk = _read(Path(registry.path))
    assert on_disk["ghost"]["command"] == ["/bin/echo", "hello"]


def test_register_rejects_duplicate_and_incomplete(registry: ModuleRegistry) -> None:
    with pytest.raises(ValueError, match="already registered"):
        registry.register("qa", _complete_entry())

    with pytest.raises(RegistrySchemaError, match="command"):
        registry.register("no-command", {"status": "enabled", "transport": "stdio"})

    with pytest.raises(RegistrySchemaError, match="unknown field"):
        registry.register("junk", {**_complete_entry(), "bogus": 1})


# ── A2: patch-only update ────────────────────────────────────────────


def test_update_is_patch_only_and_never_creates(registry: ModuleRegistry) -> None:
    with pytest.raises(ValueError, match="not found in registry"):
        registry.update("does-not-exist", "enabled")

    before = registry.module_config("qa")
    assert before is not None
    registry.update("qa", "disabled", description="paused")
    after = registry.module_config("qa")
    assert after is not None
    assert after["status"] == "disabled"
    assert after["description"] == "paused"
    # Untouched fields survive the patch.
    assert after["transport"] == before["transport"]
    assert after["command"] == before["command"]
    assert "does-not-exist" not in _read(Path(registry.path))


def test_update_patches_command_and_transport(registry: ModuleRegistry) -> None:
    registry.update("qa", "enabled", command=["/bin/echo", "patched"], transport="stdio")

    entry = registry.module_config("qa")
    assert entry is not None
    assert entry["command"] == ["/bin/echo", "patched"]
    assert entry["transport"] == "stdio"
    # The patch touched the tracked config, not the state file.
    assert not Path(registry.state_path).exists()


# ── A3: orphan state tolerated and pruned ────────────────────────────


def test_status_tolerates_orphan_state_then_prunes_it(registry: ModuleRegistry) -> None:
    Path(registry.state_path).parent.mkdir(parents=True, exist_ok=True)
    Path(registry.state_path).write_text(
        json.dumps({"ghost": _state_entry(), "qa": _state_entry()}), encoding="utf-8"
    )

    status = registry.status()
    assert status["valid"] is True
    assert status["state_error"] is None
    assert status["stale_state"] == ["ghost"]
    assert any("ghost" in warning for warning in status["warnings"])
    assert "ghost" not in status["modules"]
    assert status["modules"]["qa"]["status"] == "connected"

    registry.record_runtime_state("qa", "connected")
    state = _read(Path(registry.state_path))
    assert "ghost" not in state
    assert state["qa"]["status"] == "connected"


# ── A4: status never raises ──────────────────────────────────────────


def test_status_never_raises_on_corrupt_state(registry: ModuleRegistry) -> None:
    Path(registry.state_path).parent.mkdir(parents=True, exist_ok=True)
    Path(registry.state_path).write_text("{not json", encoding="utf-8")

    status = registry.status()

    assert status["modules"]["qa"]["status"] == "enabled"
    assert status["state_error"] is not None
    assert "not valid JSON" in status["state_error"]
    assert status["stale_state"] == []
    # State is derived: a corrupt file is a warning, never an invalid registry.
    assert status["valid"] is True
    assert status["warnings"]
    assert any("not valid JSON" in warning for warning in status["warnings"])


def test_status_keeps_legacy_contract_fields(registry: ModuleRegistry) -> None:
    status = registry.status()

    for key in (
        "registry_path",
        "state_path",
        "modules",
        "count",
        "connected_count",
        "error_count",
        "disabled_count",
        "connecting_count",
        "enabled_count",
        "last_updated",
    ):
        assert key in status, key
    assert isinstance(status["modules"], dict)
    assert isinstance(status["count"], int)
    assert status["count"] == 5
    # New keys are additive only.
    assert isinstance(status["valid"], bool)
    assert isinstance(status["errors"], list)
    assert isinstance(status["warnings"], list)
    assert isinstance(status["stale_state"], list)
    assert status["state_error"] is None
    assert status["warnings"] == []


# ── A5: validate is honest ───────────────────────────────────────────


def test_validate_missing_config_false_missing_state_true(
    registry: ModuleRegistry,
) -> None:
    Path(registry.state_path).unlink(missing_ok=True)
    valid = registry.validate()
    assert valid["valid"] is True
    assert valid["errors"] == []
    assert valid["warnings"] == []

    Path(registry.path).unlink()
    result = registry.validate()
    assert result["valid"] is False
    assert any("does not exist" in error for error in result["errors"])
    assert result["warnings"] == []


def test_validate_state_problems_are_warnings_not_errors(
    registry: ModuleRegistry,
) -> None:
    Path(registry.state_path).parent.mkdir(parents=True, exist_ok=True)

    # Root is a list: unusable state is quarantined, not fatal.
    Path(registry.state_path).write_text("[1, 2, 3]", encoding="utf-8")
    list_root = registry.validate()
    assert list_root["valid"] is True
    assert list_root["errors"] == []
    assert any("root must be an object" in w for w in list_root["warnings"])

    # Corrupt JSON is also a state problem: quarantined and self-healing.
    Path(registry.state_path).write_text("{not json", encoding="utf-8")
    corrupt = registry.validate()
    assert corrupt["valid"] is True
    assert corrupt["errors"] == []
    assert any("not valid JSON" in w for w in corrupt["warnings"])

    # A config violation is still fatal and stays in errors.
    Path(registry.state_path).write_text("{}", encoding="utf-8")
    Path(registry.path).write_text(
        json.dumps({"qa": {"status": "banana"}}), encoding="utf-8"
    )
    invalid = registry.validate()
    assert invalid["valid"] is False
    assert any("status" in error for error in invalid["errors"])
    assert invalid["warnings"] == []


def test_validate_treats_orphan_state_as_warning(registry: ModuleRegistry) -> None:
    Path(registry.state_path).parent.mkdir(parents=True, exist_ok=True)
    Path(registry.state_path).write_text(
        json.dumps({"ghost": _state_entry(), "qa": _state_entry()}), encoding="utf-8"
    )

    result = registry.validate()

    assert result["valid"] is True
    assert result["errors"] == []
    assert any("ghost" in warning for warning in result["warnings"])
    assert result["stale_state"] == ["ghost"]
    assert result["state_error"] is None


# ── A6: atomic writes + blocklist + schema_version ───────────────────


def test_json_dump_failure_leaves_old_files_parseable(
    registry: ModuleRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_before = Path(registry.path).read_text(encoding="utf-8")
    registry.record_runtime_state("qa", "connected")
    state_before = Path(registry.state_path).read_text(encoding="utf-8")

    def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(module_registry.json, "dump", boom)

    with pytest.raises(RuntimeError, match="disk full"):
        registry.update("qa", "disabled")
    with pytest.raises(RuntimeError, match="disk full"):
        registry.record_runtime_state("qa", "error", last_error="boom")

    assert Path(registry.path).read_text(encoding="utf-8") == config_before
    assert Path(registry.state_path).read_text(encoding="utf-8") == state_before
    assert _read(Path(registry.path))["qa"]["status"] == "enabled"
    assert _read(Path(registry.state_path))["qa"]["status"] == "connected"
    assert not list(Path(registry.path).parent.glob("*.tmp"))
    assert not list(Path(registry.state_path).parent.glob("*.tmp"))


def test_persistent_view_blocks_runtime_keys_and_meta_has_schema_version(
    registry: ModuleRegistry,
) -> None:
    projected = registry._persistent_view(
        {
            "status": "enabled",
            "transport": "stdio",
            "command": ["/bin/echo"],
            "description": "x",
            "last_checked": "2026-11-06T00:00:00+00:00",
            "response_time_ms": 12.0,
            "last_error": "nope",
        }
    )
    assert projected == {
        "status": "enabled",
        "transport": "stdio",
        "command": ["/bin/echo"],
        "description": "x",
    }

    registry.update("qa", "disabled")
    meta = _read(Path(registry.path))["_meta"]
    assert meta["schema_version"] == 2
    assert meta["total_modules"] == 5


def test_module_registry_validate_reports_invalid(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "module-registry.json"
    state_path = tmp_path / "state" / "module-registry.state.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    _write(config_path, {"qa": {"status": "banana"}})
    _write(state_path, {})

    registry = ModuleRegistry(registry_path=config_path, state_path=state_path)
    result = registry.validate()

    assert result["valid"] is False
    assert any("status" in e for e in result["errors"])


# ── A7: non-UTF-8 files, unreadable-config facts, stable validate shape ──

NON_UTF8_CONFIG = b'{"qa": {"description": "caf\xe9"}}'
NON_UTF8_STATE = (
    b'{"qa": {"status": "connected", '
    b'"last_checked": "2026-11-06T00:00:00+00:00", '
    b'"last_error": "caf\xe9"}}'
)


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def test_config_not_utf8_is_fatal_and_never_raises(
    registry: ModuleRegistry,
) -> None:
    _write_bytes(Path(registry.path), NON_UTF8_CONFIG)

    status = registry.status()
    assert status["valid"] is False
    assert any("UTF-8" in error for error in status["errors"])
    assert status["warnings"] == []
    assert status["modules"] == {}

    result = registry.validate()
    assert result["valid"] is False
    assert any("config corrupt" in error for error in result["errors"])
    assert any("UTF-8" in error for error in result["errors"])
    assert result["warnings"] == []

    # The registry read path converts the codec error; no caller ever sees a
    # raw UnicodeDecodeError from here (wrapping ModuleHost is C2).
    with pytest.raises(RegistrySchemaError, match="UTF-8"):
        registry.module_config("qa")


def test_state_not_utf8_is_warning_and_status_keeps_full_view(
    registry: ModuleRegistry,
) -> None:
    _write_bytes(Path(registry.state_path), NON_UTF8_STATE)

    status = registry.status()
    assert status["valid"] is True
    assert status["errors"] == []
    assert status["count"] == 5
    assert set(status["modules"]) == {
        "solocorp",
        "central-bus",
        "content-creator",
        "engineering",
        "qa",
    }
    assert status["modules"]["qa"]["status"] == "enabled"
    assert status["state_error"] is not None
    assert "UTF-8" in status["state_error"]
    assert status["stale_state"] == []
    assert any("UTF-8" in warning for warning in status["warnings"])

    result = registry.validate()
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["state_error"] is not None
    assert any("UTF-8" in warning for warning in result["warnings"])


def test_unreadable_config_reports_no_stale_state(
    registry: ModuleRegistry,
) -> None:
    _write_bytes(Path(registry.path), NON_UTF8_CONFIG)
    _write_bytes(
        Path(registry.state_path),
        json.dumps(
            {
                module_id: _state_entry()
                for module_id in ("central-bus", "qa", "solocorp")
            }
        ).encode("utf-8"),
    )

    # Without a readable config "stale" is undefined: reporting those three
    # entries as orphans would be a lie, so the registry reports nothing.
    status = registry.status()
    assert status["valid"] is False
    assert status["stale_state"] == []
    assert status["state_error"] is None

    result = registry.validate()
    assert result["valid"] is False
    assert result["stale_state"] == []
    assert result["state_error"] is None


def test_validate_returns_five_keys_on_every_path(
    registry: ModuleRegistry,
) -> None:
    expected = {"valid", "errors", "warnings", "stale_state", "state_error"}

    assert set(registry.validate()) == expected

    _write_bytes(Path(registry.state_path), b"\xff")
    assert set(registry.validate()) == expected

    _write_bytes(Path(registry.path), NON_UTF8_CONFIG)
    assert set(registry.validate()) == expected

    Path(registry.path).unlink()
    missing = registry.validate()
    assert set(missing) == expected
    assert missing["stale_state"] == []
    assert missing["state_error"] is None
