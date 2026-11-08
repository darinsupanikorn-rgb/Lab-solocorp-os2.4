"""Module registry for SoloCorp department MCP modules.

Two files, two lifetimes:

* **Config** (``config/module-registry.json``, git-tracked) — what the human
  decided: which modules exist, their transport, command and whether they are
  enabled or disabled. Changes only when a person changes it.
* **State** (``central_bus/module-registry.state.json``, git-ignored) — what
  the runtime observed: ``connecting`` / ``connected`` / ``error``,
  ``last_checked``, ``response_time_ms``, ``last_error``. Written on every
  heartbeat.

Keeping them apart means a health check never dirties a tracked file. The
public read model (``status()``) still returns one merged view per module, so
callers see ``enabled``/``disabled`` plus live connection detail as before.

C1 review policy (CEO, 2026-11-06) — accepted, not deferred bugs:

* **Logical quarantine** of a corrupt state file means the read path ignores it
  in place; it never renames the file to ``.corrupt``. Reading must not write.
* ``update()`` requires an explicit ``status`` on every call. This is an
  accepted limitation until C2; the UI toggle already sends ``status``.
* Physical quarantine, file locking and HTTP transport are C2+, not C1.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .module_registry_schema import (
    PERSISTENT_STATUSES,
    RUNTIME_STATUSES,
    SCHEMA_VERSION,
    RegistrySchemaError,
    load_and_validate_config,
    read_json_document,
    validate_config,
    validate_config_module,
    validate_state,
)

from .auth import SCOPE_LEVELS

ROOT = Path(__file__).resolve().parent.parent

# Tracked config — belongs in git.
DEFAULT_CONFIG_PATH = ROOT / "config" / "module-registry.json"

# Runtime observation — never in git.
DEFAULT_STATE_PATH = ROOT / "central_bus" / "module-registry.state.json"

# Backwards-compatible alias: the registry file used before the split.
LEGACY_REGISTRY_PATH = ROOT / "central_bus" / "content" / "module-registry.json"

# Statuses that describe intent and therefore live in the tracked config.
VALID_STATUSES = PERSISTENT_STATUSES | RUNTIME_STATUSES

# Runtime observations never belong in the tracked config. This is a blocklist
# (not an allowlist): unknown fields survive projection and then fail schema
# validation loudly instead of being silently dropped.
RUNTIME_ONLY_FIELDS = frozenset({"last_checked", "response_time_ms", "last_error"})

DEFAULT_MODULES: dict[str, dict[str, Any]] = {
    "solocorp": {
        "status": "enabled",
        "transport": "stdio",
        "command": [".venv/bin/python3", "-m", "solocorp_mcp.server"],
        "description": "Core MCP — Organization & Routing",
    },
    "central-bus": {
        "status": "enabled",
        "transport": "stdio",
        "command": [".venv/bin/python3", "-m", "solocorp_mcp.bus_mcp"],
        "description": "Central Bus — Storage & Queue",
    },
    "content-creator": {
        "status": "enabled",
        "transport": "stdio",
        "command": [".venv/bin/python3", "-m", "solocorp_mcp.departments.content_mcp"],
        "description": "Content Creator Department",
    },
    "engineering": {
        "status": "enabled",
        "transport": "stdio",
        "command": [".venv/bin/python3", "-m", "solocorp_mcp.departments.engineering_mcp"],
        "description": "Engineering Department",
    },
    "qa": {
        "status": "enabled",
        "transport": "stdio",
        "command": [".venv/bin/python3", "-m", "solocorp_mcp.departments.qa_mcp"],
        "description": "QA Department",
    },
}


@dataclass(frozen=True)
class _StateRead:
    """Result of a tolerant state read (never raises)."""

    entries: dict[str, dict[str, Any]]
    stale: list[str]
    error: str | None


def _state_warnings(state: _StateRead) -> list[str]:
    """Render derived-state problems as warnings (they never invalidate config)."""

    warnings: list[str] = []
    if state.stale:
        warnings.append(
            "state orphan: " + ", ".join(state.stale) + " not declared in config"
        )
    if state.error is not None:
        warnings.append(f"state invalid: {state.error}")
    return warnings


def _permissions_warnings(config: dict[str, dict[str, Any]]) -> list[str]:
    """Warn when a module declares a permission scope not yet in SCOPE_LEVELS.

    Fail-open: the value is kept and the module still loads. This is a
    declarative-metadata warning only — it never enforces or blocks anything
    (permissions is metadata, not a caller gate; ``require_scope`` is untouched).
    """

    warnings: list[str] = []
    for module_id, entry in config.items():
        perms = entry.get("permissions")
        if isinstance(perms, list):
            for item in perms:
                if isinstance(item, str) and item not in SCOPE_LEVELS:
                    warnings.append(
                        f"module '{module_id}': permission scope {item!r} "
                        f"not in SCOPE_LEVELS (kept, fail-open)"
                    )
    return warnings


class ModuleRegistry:
    """Read/write module config and connection state from two separate files."""

    def __init__(
        self,
        registry_path: Path | None = None,
        state_path: Path | None = None,
    ) -> None:
        self.path = Path(registry_path) if registry_path else DEFAULT_CONFIG_PATH
        self.state_path = Path(state_path) if state_path else DEFAULT_STATE_PATH
        self._ensure_initialized()

    # ------------------------------------------------------------------ setup

    def _ensure_initialized(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            errors = validate_config(DEFAULT_MODULES)
            if errors:
                raise RegistrySchemaError(
                    f"default modules violate schema: {'; '.join(errors)}"
                )
            self._save_config(DEFAULT_MODULES)

    # ------------------------------------------------------------------- i/o

    def _save_config(self, modules: dict[str, Any]) -> None:
        errors = validate_config(modules)
        if errors:
            raise RegistrySchemaError(
                f"config violates schema: {'; '.join(errors)}"
            )
        data = {
            module_id: self._persistent_view(entry)
            for module_id, entry in modules.items()
            if module_id != "_meta"
        }
        data["_meta"] = {
            "last_updated": self._now(),
            "total_modules": len(data),
            "schema_version": SCHEMA_VERSION,
        }
        self._atomic_write_json(self.path, data)

    def _save_state(self, state: dict[str, Any]) -> None:
        config_ids = set(self._load_config().keys())
        # State is derived data: drop observations for modules removed from
        # config *before* validating, so a stale entry can never block the
        # next heartbeat (and is pruned from disk on this write).
        pruned = {
            module_id: entry
            for module_id, entry in state.items()
            if module_id != "_meta" and module_id in config_ids
        }
        errors = validate_state(pruned, config_ids)
        if errors:
            raise RegistrySchemaError(
                f"state violates schema: {'; '.join(errors)}"
            )
        data = dict(pruned)
        data["_meta"] = {
            "last_updated": self._now(),
            "total_modules": len(pruned),
            "schema_version": SCHEMA_VERSION,
        }
        self._atomic_write_json(self.state_path, data)

    def _atomic_write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Write JSON to a sibling temp file, then ``os.replace`` it.

        A crash or ``json.dump`` failure mid-write leaves the previous file
        intact and parseable; the temp file is removed on failure.
        """

        path.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        )
        temp_path = Path(handle.name)
        try:
            with handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        except BaseException:
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise

    def _load_config(self) -> dict[str, Any]:
        data = load_and_validate_config(self.path)
        return {
            key: value
            for key, value in data.items()
            if key != "_meta"
        }

    def _config_meta(self) -> dict[str, Any]:
        """Best-effort ``_meta`` read for status; never raises."""

        try:
            document = read_json_document(self.path)
        except RegistrySchemaError:
            return {}
        if not isinstance(document, dict):
            return {}
        meta = document.get("_meta")
        return meta if isinstance(meta, dict) else {}

    def _read_state(self, config_ids: set[str]) -> _StateRead:
        """Tolerant state read: never raises, quarantines unusable state.

        Orphan entries (a module removed from config) are dropped and reported
        in ``stale``. Any other schema violation quarantines the whole state
        file — state is derived data — and is reported in ``error``.
        """

        try:
            document = read_json_document(self.state_path)
        except RegistrySchemaError as exc:
            return _StateRead({}, [], str(exc))
        if document is None:
            if self.state_path.exists():
                return _StateRead({}, [], "state root must be an object")
            return _StateRead({}, [], None)
        if not isinstance(document, dict):
            return _StateRead({}, [], "state root must be an object")

        entries = {
            module_id: entry
            for module_id, entry in document.items()
            if module_id != "_meta"
        }
        stale = sorted(
            module_id for module_id in entries if module_id not in config_ids
        )
        for module_id in stale:
            del entries[module_id]

        errors = validate_state(entries, config_ids)
        if errors:
            return _StateRead({}, stale, "; ".join(errors))
        return _StateRead(entries, stale, None)

    def _load_state(self) -> dict[str, Any]:
        return self._read_state(set(self._load_config())).entries

    @staticmethod
    def _persistent_view(entry: dict[str, Any]) -> dict[str, Any]:
        """Strip runtime observations so they never reach the tracked file."""

        return {
            key: value
            for key, value in entry.items()
            if key not in RUNTIME_ONLY_FIELDS
        }

    def _merged(
        self,
        config: dict[str, dict[str, Any]],
        state: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Config entry + runtime observation, runtime wins for live fields."""

        merged = {key: dict(value) for key, value in config.items()}
        for module_id, entry in state.items():
            if module_id not in merged:
                continue
            merged[module_id].update(
                {key: value for key, value in entry.items() if value is not None}
            )
        return merged

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------------- read API

    def status(self) -> dict[str, Any]:
        """Return the merged view of every module with summary statistics.

        Never raises: config problems appear in ``errors`` and make ``valid``
        false; derived-state problems appear in ``warnings`` (and as
        ``stale_state``/``state_error``). Config errors invalidate the
        registry; state problems are warnings because state is derived and
        rewritten by the next heartbeat. When the config cannot be read the
        state file cannot be interpreted either — "stale" is undefined without
        a module list — so ``stale_state``/``state_error`` stay empty rather
        than labelling every entry an orphan. The original fields keep their
        names and shapes; the new keys are additive.
        """

        errors: list[str] = []
        config: dict[str, dict[str, Any]] = {}
        if not self.path.exists():
            errors.append(f"config file {self.path} does not exist")
        else:
            try:
                config = self._load_config()
            except RegistrySchemaError as exc:
                errors.append(str(exc))

        if errors:
            # No readable config means no trustworthy module set. Reading state
            # against an empty set would report every entry as stale, which is
            # a lie: we simply do not know.
            state = _StateRead({}, [], None)
        else:
            state = self._read_state(set(config))
        modules = self._merged(config, state.entries)
        meta = self._config_meta()
        warnings = [] if errors else _state_warnings(state)
        if not errors:
            warnings.extend(_permissions_warnings(config))

        def count(status: str) -> int:
            return sum(
                1 for value in modules.values() if value.get("status") == status
            )

        return {
            "registry_path": str(self.path),
            "state_path": str(self.state_path),
            "modules": modules,
            "count": len(modules),
            "connected_count": count("connected"),
            "error_count": count("error"),
            "disabled_count": count("disabled"),
            "connecting_count": count("connecting"),
            "enabled_count": count("enabled"),
            "last_updated": meta.get("last_updated", "never"),
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "stale_state": state.stale,
            "state_error": state.error,
        }

    def module_config(self, module_id: str) -> dict[str, Any] | None:
        """Return one module's configured intent, without runtime observations."""

        entry = self._load_config().get(module_id)
        return dict(entry) if isinstance(entry, dict) else None

    def validate(self) -> dict[str, Any]:
        """Validate config and state, separating fatal from derived problems.

        Config errors invalidate the registry; state problems are warnings
        because state is derived and rewritten by the next heartbeat. Missing
        state is fine. ``warnings`` mirrors ``stale_state``/``state_error`` so
        this result and ``status()`` describe the same condition in the same
        words. Returns the same five keys on every path: when the config
        cannot be read, ``stale_state`` is ``[]`` and ``state_error`` is
        ``None`` because neither can be derived without a module list. Never
        raises.
        """

        if not self.path.exists():
            return {
                "valid": False,
                "errors": [f"config file {self.path} does not exist"],
                "warnings": [],
                "stale_state": [],
                "state_error": None,
            }

        try:
            config = load_and_validate_config(self.path)
        except RegistrySchemaError as exc:
            message = str(exc)
            corrupt = "not valid JSON" in message or "not valid UTF-8" in message
            kind = "corrupt" if corrupt else "invalid"
            return {
                "valid": False,
                "errors": [f"config {kind}: {message}"],
                "warnings": [],
                "stale_state": [],
                "state_error": None,
            }

        state = self._read_state(
            {module_id for module_id in config if module_id != "_meta"}
        )
        return {
            "valid": True,
            "errors": [],
            "warnings": _state_warnings(state),
            "stale_state": state.stale,
            "state_error": state.error,
        }

    # --------------------------------------------------------------- write API

    def register(self, module_id: str, entry: dict[str, Any]) -> dict[str, Any]:
        """Register a new module. Requires a complete config entry.

        The entry must satisfy the config schema for its transport; nothing is
        defaulted or invented here. Raises ``ValueError`` when the module
        already exists and ``RegistrySchemaError`` when the entry is invalid.
        """

        if not isinstance(module_id, str) or not module_id.strip():
            raise ValueError("module_id must be a non-empty string")

        modules = self._load_config()
        if module_id in modules:
            raise ValueError(f"module {module_id} already registered")

        errors = validate_config_module(module_id, entry)
        if errors:
            raise RegistrySchemaError(
                f"entry for module {module_id} violates schema: {'; '.join(errors)}"
            )

        modules[module_id] = dict(entry)
        self._save_config(modules)
        return {"module_id": module_id, **dict(entry)}

    def update(
        self,
        module_id: str,
        status: str,
        description: str | None = None,
        *,
        command: list[str] | None = None,
        transport: str | None = None,
    ) -> dict[str, Any]:
        """Patch one existing module; never creates a module.

        ``enabled``/``disabled`` change the tracked config. A runtime status
        (``connected``/``connecting``/``error``) is an observation, so it is
        written to the state file instead — the tracked config never carries
        a heartbeat result. Only the fields that are passed are changed.
        """

        if status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )

        modules = self._load_config()
        if module_id not in modules:
            raise ValueError(f"module {module_id} not found in registry")
        previous = modules[module_id]

        if status in RUNTIME_STATUSES:
            if command is not None or transport is not None:
                raise ValueError(
                    "command/transport can only be patched with a persistent status"
                )
            self.record_runtime_state(module_id, status)
            return {
                "module_id": module_id,
                "status": status,
                "description": previous.get("description", ""),
                "updated": True,
            }

        patched = dict(previous)
        patched["status"] = status
        if description is not None:
            patched["description"] = description
        if command is not None:
            patched["command"] = list(command)
        if transport is not None:
            patched["transport"] = transport
        patched["updated_at"] = self._now()

        modules[module_id] = patched
        self._save_config(modules)
        return {
            "module_id": module_id,
            "status": patched["status"],
            "description": patched.get("description", ""),
            "transport": patched.get("transport"),
            "command": patched.get("command"),
            "updated": True,
        }

    def record_runtime_state(
        self,
        module_id: str,
        status: str,
        response_time_ms: float | None = None,
        last_error: str | None = None,
    ) -> None:
        """Persist a runtime observation without changing configured intent."""

        if status not in RUNTIME_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(RUNTIME_STATUSES))}"
            )
        if module_id not in self._load_config():
            raise ValueError(f"module {module_id} not found in registry")
        self._record_state(module_id, status, response_time_ms, last_error)

    def clear_runtime_state(self, module_id: str) -> None:
        """Remove observations so status falls back to configured intent."""

        if module_id not in self._load_config():
            raise ValueError(f"module {module_id} not found in registry")
        state = self._load_state()
        if module_id in state:
            del state[module_id]
            self._save_state(state)

    def heartbeat(self, module_id: str, timeout: float = 5.0) -> dict[str, Any]:
        """Attempt a real stdio connection and record the result in state only."""

        import time

        from .departments.mcp_stdio import MCPStdioClient, MCPStdioError

        modules = self._load_config()
        if module_id not in modules:
            raise ValueError(f"module {module_id} not found in registry")

        entry = modules[module_id]
        # The config schema requires a non-empty command list for stdio, so
        # there is no "missing command" branch here. ModuleHost keeps that
        # guard for callers that pass their own config dict.
        command = entry["command"]

        self._record_state(module_id, status="connecting")

        start = time.perf_counter()
        client = None
        try:
            client = MCPStdioClient(
                command,
                cwd=str(ROOT),
                startup_timeout=timeout,
            )
            # Call list_tools as a lightweight connectivity check
            client.request("tools/list", {}, timeout=timeout)
            elapsed_ms = (time.perf_counter() - start) * 1000

            status = "connected"
            connected = True
            error = None
            self._record_state(
                module_id,
                status=status,
                response_time_ms=round(elapsed_ms, 2),
                last_error=None,
            )
        except MCPStdioError as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = "error"
            connected = False
            error = str(exc)[:200]
            self._record_state(
                module_id,
                status=status,
                response_time_ms=round(elapsed_ms, 2),
                last_error=error,
            )
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = "error"
            connected = False
            error = f"{type(exc).__name__}: {str(exc)[:200]}"
            self._record_state(
                module_id,
                status=status,
                response_time_ms=round(elapsed_ms, 2),
                last_error=error,
            )
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:  # noqa: BLE001
                    pass

        return {
            "module_id": module_id,
            "status": status,
            "connected": connected,
            "error": error,
            "response_time_ms": self._load_state().get(module_id, {}).get(
                "response_time_ms"
            ),
        }

    def _record_state(
        self,
        module_id: str,
        status: str,
        response_time_ms: float | None = None,
        last_error: str | None = None,
    ) -> None:
        state = self._load_state()
        entry = {
            **_runtime_entry_defaults(state.get(module_id, {})),
            "status": status,
            "last_checked": self._now(),
        }
        if response_time_ms is not None:
            entry["response_time_ms"] = response_time_ms
        if last_error is not None or status in ("connected", "connecting"):
            entry["last_error"] = last_error
        state[module_id] = entry
        self._save_state(state)


def _runtime_entry_defaults(previous: dict[str, Any]) -> dict[str, Any]:
    return {
        "response_time_ms": previous.get("response_time_ms"),
        "last_error": previous.get("last_error"),
    }
