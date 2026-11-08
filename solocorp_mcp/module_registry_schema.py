"""Schema and validation for module registry config and state files.

Locks the shape of:

* ``config/module-registry.json`` — human intent (enabled/disabled, transport,
  command, description). Changes only when a person changes it.
* ``central_bus/module-registry.state.json`` — runtime observation
  (connected/connecting/error, last_checked, response_time_ms, last_error).
  Written on every heartbeat.

No external dependencies: pure Python validation so the registry never needs
an extra library just to read its own config. A corrupted or hand-edited file
is rejected loudly rather than silently misinterpreted.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .auth import SCOPE_LEVELS

# --- Schema constants -----------------------------------------------------

# Statuses that describe intent and therefore live in the tracked config.
PERSISTENT_STATUSES = frozenset({"enabled", "disabled"})

# Statuses that describe an observation and therefore live in the state file.
RUNTIME_STATUSES = frozenset({"connected", "connecting", "error"})

VALID_STATUSES = PERSISTENT_STATUSES | RUNTIME_STATUSES

# Transport values allowed in config.
VALID_TRANSPORTS = frozenset({"stdio"})

# Capability allow-list (standard MCP capability groups).
VALID_CAPABILITIES = frozenset({"tools", "resources", "prompts"})

# Field names per file layer.
CONFIG_REQUIRED_FIELDS = frozenset({"status", "transport", "command"})
CONFIG_OPTIONAL_FIELDS = frozenset(
    {"description", "updated_at", "permissions", "version", "capabilities", "dependencies", "entry_repo"}
)
CONFIG_ALL_FIELDS = CONFIG_REQUIRED_FIELDS | CONFIG_OPTIONAL_FIELDS

STATE_REQUIRED_FIELDS = frozenset({"status", "last_checked"})
STATE_OPTIONAL_FIELDS = frozenset({"response_time_ms", "last_error"})
STATE_ALL_FIELDS = STATE_REQUIRED_FIELDS | STATE_OPTIONAL_FIELDS

META_FIELDS = frozenset({"last_updated", "total_modules", "schema_version"})

# Bump when the on-disk shape changes in a way old readers cannot accept.
SCHEMA_VERSION = 2

# --- Errors ---------------------------------------------------------------


class RegistrySchemaError(ValueError):
    """Raised when a registry file violates its schema."""


# --- Helpers --------------------------------------------------------------


def _is_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def _non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(isinstance(item, str) and item for item in value)
    )


def _string_list(value: Any) -> bool:
    """List of non-empty strings; empty list allowed, duplicates allowed."""
    return isinstance(value, list) and all(
        isinstance(item, str) and item for item in value
    )


def _unique_string_list(value: Any) -> bool:
    """List of non-empty strings with no duplicates; empty list allowed."""
    return _string_list(value) and len(value) == len(set(value))


def validate_meta(meta: Any, file_label: str) -> list[str]:
    """Validate a file-level ``_meta`` block. Missing ``_meta`` is allowed."""

    if meta is None:
        return []
    if not isinstance(meta, dict):
        return [f"{file_label} _meta: must be an object"]

    prefix = f"{file_label} _meta"
    errors: list[str] = []

    for key in meta:
        if key not in META_FIELDS:
            errors.append(f"{prefix}: unknown field '{key}'")

    if "last_updated" in meta and not _is_iso_timestamp(meta["last_updated"]):
        errors.append(f"{prefix}: last_updated must be an ISO 8601 timestamp")

    if "total_modules" in meta:
        value = meta["total_modules"]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errors.append(f"{prefix}: total_modules must be a non-negative integer")

    if "schema_version" in meta and meta["schema_version"] != SCHEMA_VERSION:
        errors.append(
            f"{prefix}: schema_version must be {SCHEMA_VERSION}, "
            f"got {meta['schema_version']!r}"
        )

    return errors


# --- Per-module validation ------------------------------------------------


def validate_config_module(module_id: str, entry: Any) -> list[str]:
    """Validate one config module entry. Returns a list of error messages."""

    errors: list[str] = []
    prefix = f"config module '{module_id}'"

    if not isinstance(entry, dict):
        errors.append(f"{prefix}: must be an object, got {type(entry).__name__}")
        return errors

    # Unknown fields.
    for key in entry:
        if key not in CONFIG_ALL_FIELDS:
            errors.append(f"{prefix}: unknown field '{key}'")

    # Required fields.
    for field in CONFIG_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{prefix}: missing required field '{field}'")

    # status.
    if "status" in entry and entry["status"] not in PERSISTENT_STATUSES:
        errors.append(
            f"{prefix}: status must be one of {sorted(PERSISTENT_STATUSES)}, "
            f"got {entry['status']!r}"
        )

    # transport.
    if "transport" in entry and entry["transport"] not in VALID_TRANSPORTS:
        errors.append(
            f"{prefix}: transport must be one of {sorted(VALID_TRANSPORTS)}, "
            f"got {entry['transport']!r}"
        )

    # command.
    if "command" in entry and not _non_empty_string_list(entry["command"]):
        errors.append(
            f"{prefix}: command must be a non-empty list of non-empty strings"
        )

    # description.
    if "description" in entry and not isinstance(entry["description"], str):
        errors.append(f"{prefix}: description must be a string")

    # updated_at.
    if "updated_at" in entry and not _is_iso_timestamp(entry["updated_at"]):
        errors.append(f"{prefix}: updated_at must be an ISO 8601 timestamp")

    # permissions — declarative metadata, NOT a caller gate.
    # Structural violations are errors; unknown scope items are fail-open
    # (kept, module still loads — warning reported at registry layer).
    if "permissions" in entry:
        perms = entry["permissions"]
        if not _unique_string_list(perms):
            errors.append(
                f"{prefix}: permissions must be a list of non-empty unique strings"
            )
        else:
            for item in perms:
                if item not in SCOPE_LEVELS:
                    # Unknown scope: kept as-is, fail-open. Not a fatal error.
                    pass

    # version — declarative, non-empty string when present.
    if "version" in entry:
        version_value = entry["version"]
        if not isinstance(version_value, str) or not version_value.strip():
            errors.append(f"{prefix}: version must be a non-empty string")

    # capabilities — allow-list {"tools","resources","prompts"}.
    if "capabilities" in entry:
        caps = entry["capabilities"]
        if not _unique_string_list(caps):
            errors.append(
                f"{prefix}: capabilities must be a list of non-empty unique strings"
            )
        else:
            for item in caps:
                if item not in VALID_CAPABILITIES:
                    errors.append(
                        f"{prefix}: capabilities item {item!r} not in "
                        f"{sorted(VALID_CAPABILITIES)}"
                    )

    # dependencies — list of non-empty unique strings, no self-dependency.
    if "dependencies" in entry:
        deps = entry["dependencies"]
        if not _unique_string_list(deps):
            errors.append(
                f"{prefix}: dependencies must be a list of non-empty unique strings"
            )
        else:
            if module_id in deps:
                errors.append(
                    f"{prefix}: dependencies must not include self ('{module_id}')"
                )

    # entry_repo — non-empty string ("internal" | relative path | absolute URL).
    if "entry_repo" in entry:
        repo = entry["entry_repo"]
        if not isinstance(repo, str) or not repo.strip():
            errors.append(f"{prefix}: entry_repo must be a non-empty string")

    return errors


def validate_state_module(
    module_id: str, entry: Any, known_modules: set[str]
) -> list[str]:
    """Validate one state module entry."""

    errors: list[str] = []
    prefix = f"state module '{module_id}'"

    if module_id not in known_modules:
        errors.append(f"{prefix}: module not declared in config")

    if not isinstance(entry, dict):
        errors.append(f"{prefix}: must be an object, got {type(entry).__name__}")
        return errors

    # Unknown fields.
    for key in entry:
        if key not in STATE_ALL_FIELDS:
            errors.append(f"{prefix}: unknown field '{key}'")

    # Required fields.
    for field in STATE_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{prefix}: missing required field '{field}'")

    # status.
    if "status" in entry and entry["status"] not in RUNTIME_STATUSES:
        errors.append(
            f"{prefix}: status must be one of {sorted(RUNTIME_STATUSES)}, "
            f"got {entry['status']!r}"
        )

    # last_checked.
    if "last_checked" in entry and not _is_iso_timestamp(entry["last_checked"]):
        errors.append(f"{prefix}: last_checked must be an ISO 8601 timestamp")

    # response_time_ms.
    if "response_time_ms" in entry:
        value = entry["response_time_ms"]
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"{prefix}: response_time_ms must be a number or null")

    # last_error.
    if "last_error" in entry and not isinstance(
        entry["last_error"], (str, type(None))
    ):
        errors.append(f"{prefix}: last_error must be a string or null")

    return errors


# --- Whole-file validation ------------------------------------------------


def validate_config(modules: Any) -> list[str]:
    """Validate an entire config mapping (module_id -> entry)."""

    errors: list[str] = []

    if not isinstance(modules, dict):
        errors.append("config root must be an object")
        return errors

    for module_id, entry in modules.items():
        if module_id == "_meta":
            continue
        errors.extend(validate_config_module(module_id, entry))

    errors.extend(validate_meta(modules.get("_meta"), "config"))

    return errors


def validate_state(
    state: Any, config_module_ids: set[str]
) -> list[str]:
    """Validate an entire state mapping against known config modules."""

    errors: list[str] = []

    if not isinstance(state, dict):
        errors.append("state root must be an object")
        return errors

    for module_id, entry in state.items():
        if module_id == "_meta":
            continue
        errors.extend(validate_state_module(module_id, entry, config_module_ids))

    errors.extend(validate_meta(state.get("_meta"), "state"))

    return errors


def validate_merged(config: dict[str, Any], state: dict[str, Any]) -> list[str]:
    """Cross-validate config + state together."""

    errors: list[str] = validate_config(config)

    config_ids = {
        module_id
        for module_id, entry in config.items()
        if module_id != "_meta" and isinstance(entry, dict)
    }

    errors.extend(validate_state(state, config_ids))

    return errors


# --- Load + validate helpers ----------------------------------------------


def read_json_document(path: Path) -> Any | None:
    """Read a JSON document.

    Returns ``None`` when the file does not exist (first run); raises
    ``RegistrySchemaError`` when the file exists but is not valid JSON or is
    not UTF-8. ``UnicodeDecodeError`` is a ``ValueError`` (not an
    ``OSError``/``JSONDecodeError``), so it needs its own handler: callers of
    this module only ever expect ``RegistrySchemaError`` from a bad read.
    """

    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as exc:
        raise RegistrySchemaError(f"{path} is not valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RegistrySchemaError(f"{path} is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise RegistrySchemaError(f"{path} cannot be read: {exc}") from exc


def load_and_validate_config(path: Path) -> dict[str, Any]:
    """Load config JSON and validate it.

    Raises ``RegistrySchemaError`` on violation. Returns ``{}`` if the file
    does not exist yet (first run).
    """

    data = read_json_document(path)
    if data is None:
        if path.exists():
            raise RegistrySchemaError(f"{path} root must be an object")
        return {}

    errors = validate_config(data)
    if errors:
        raise RegistrySchemaError("; ".join(errors))

    return data
