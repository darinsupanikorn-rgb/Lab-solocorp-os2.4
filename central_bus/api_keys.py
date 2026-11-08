"""Central Bus — Department API Keys Management

แต่ละ Agent มี key ของตัวเอง — ใช้验证ตัวตนตอนเรียก Central Bus API

Key Format: sk-{department}-{random16}
Example:    sk-cfo-meetoo-a1b2c3d4e5f6g7h8
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Any, Optional

from central_bus.db import new_id

log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

KEY_PREFIX = "sk"
SCOPES = {"admin", "dept", "readonly"}
DEFAULT_SCOPE = "dept"
KEY_BYTE_LENGTH = 16  # 16 bytes → 32 hex chars


# ── Key Generation ────────────────────────────────────────────────────


def generate_key(agent_id: str) -> tuple[str, str]:
    """Generate a new API key for an agent.

    Returns (full_key, key_hash)
    - full_key: sk-{agent_id}-{random_hex}  —  ให้ agent เก็บไว้
    - key_hash: SHA-256 hash —  เก็บใน DB
    """
    random_part = secrets.token_hex(KEY_BYTE_LENGTH)
    full_key = f"{KEY_PREFIX}-{agent_id}-{random_part}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, key_hash


def extract_agent_from_key(full_key: str) -> Optional[str]:
    """Extract agent_id from a full key string. Returns None if invalid format."""
    parts = full_key.split("-")
    if len(parts) < 3 or parts[0] != KEY_PREFIX:
        return None
    # agent_id is everything between first and last part
    # sk-{agent_id}-{random}
    # But agent_id might contain hyphens (like "content-creator-sek")
    # So agent_id = parts[1:-1] joined
    agent_id = "-".join(parts[1:-1])
    return agent_id if agent_id else None


def hash_key(full_key: str) -> str:
    """Hash a full key for storage/validation."""
    return hashlib.sha256(full_key.encode()).hexdigest()


# ── Database Operations ──────────────────────────────────────────────


async def create_api_key(
    db: Any,
    agent_id: str,
    department_id: str,
    department_name: str,
    *,
    scope: str = DEFAULT_SCOPE,
    description: str = "",
    created_by: str = "ceo-hanuman",
) -> dict[str, Any]:
    """Create a new API key for a department agent.

    Returns dict with 'full_key' (show once) and 'key_data' (stored).
    """
    if scope not in SCOPES:
        scope = DEFAULT_SCOPE

    full_key, key_hash = generate_key(agent_id)
    key_id = new_id()
    key_prefix = f"{KEY_PREFIX}-{agent_id}"

    now = datetime.now(timezone.utc).isoformat()

    await db.execute(
        """
        INSERT INTO api_keys
            (id, key_prefix, key_hash, department_id, department_name,
             agent_id, scope, description, enabled, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (key_id, key_prefix, key_hash, department_id, department_name,
         agent_id, scope, description, now, created_by),
    )

    key_data = {
        "id": key_id,
        "key_prefix": key_prefix,
        "department_id": department_id,
        "department_name": department_name,
        "agent_id": agent_id,
        "scope": scope,
        "description": description,
        "enabled": True,
        "created_at": now,
    }

    log.info(f"🔑 Created API key for {agent_id} (scope={scope})")
    return {"full_key": full_key, "key_data": key_data}


async def validate_key(db: Any, full_key: str) -> Optional[dict[str, Any]]:
    """Validate an API key. Returns key data if valid, None if invalid."""
    agent_id = extract_agent_from_key(full_key)
    if not agent_id:
        return None

    key_hash = hash_key(full_key)

    row = await db.fetch_one(
        """
        SELECT * FROM api_keys
        WHERE key_hash = ? AND enabled = 1
        """,
        (key_hash,),
    )
    if not row:
        return None

    # Check expiry
    expires_at = row["expires_at"]
    if expires_at:
        try:
            exp = datetime.fromisoformat(expires_at)
            if exp < datetime.now(timezone.utc):
                log.warning(f"🔑 Expired key for {agent_id}")
                return None
        except ValueError:
            pass

    return dict(row)


async def list_api_keys(
    db: Any,
    *,
    department_id: Optional[str] = None,
    enabled_only: bool = True,
) -> list[dict[str, Any]]:
    """List all API keys, optionally filtered."""
    conditions = []
    params: list[Any] = []

    if department_id:
        conditions.append("department_id = ?")
        params.append(department_id)
    if enabled_only:
        conditions.append("enabled = 1")

    where = " AND ".join(conditions) if conditions else "1=1"
    rows = await db.fetch_all(
        f"SELECT id, key_prefix, department_id, department_name, agent_id, scope, description, enabled, created_at, expires_at, created_by FROM api_keys WHERE {where} ORDER BY department_id",
        tuple(params),
    )
    return [dict(r) for r in rows]


async def revoke_api_key(db: Any, key_id: str) -> bool:
    """Disable an API key."""
    row = await db.fetch_one(
        "UPDATE api_keys SET enabled = 0 WHERE id = ? RETURNING id",
        (key_id,),
    )
    return row is not None


async def count_api_keys(db: Any) -> int:
    """Count active API keys."""
    row = await db.fetch_one("SELECT COUNT(*) as cnt FROM api_keys WHERE enabled = 1")
    return row["cnt"] if row else 0
