# 🧩 SkillHub Integration — SoloCorp OS

> Self-hosted Agent Skill Registry สำหรับจัดการ Skill packages ทั้งองค์กร  
> Forked from [iflytek/skillhub](https://github.com/iflytek/skillhub) → [Dr-SoloDev/skillhub](https://github.com/Dr-SoloDev/skillhub)  
> License: Apache 2.0

---

## สารบัญ

1. [What is SkillHub?](#1-what-is-skillhub)
2. [Why SoloCorp Needs This](#2-why-solocorp-needs-this)
3. [Architecture Overview](#3-architecture-overview)
4. [Namespaces for SoloCorp](#4-namespaces-for-solocorp)
5. [Running SkillHub](#5-running-skillhub)
6. [CLI Usage](#6-cli-usage)
7. [Integration Points](#7-integration-points)
8. [Skill Lifecycle Policy](#8-skill-lifecycle-policy)
9. [Security & Access Control](#9-security--access-control)

---

## 1. What is SkillHub?

SkillHub คือ **Agent Skill Registry** แบบ Self-hosted ที่ให้ทีมในองค์กร:

| ความสามารถ | รายละเอียด |
|:-----------|:------------|
| **Publish** | อัปโหลด skill packages (SKILL.md + assets) ด้วย semantic versioning |
| **Discover** | ค้นหาด้วย full-text search + filters (namespace, tags, downloads) |
| **Version** | semver + tags (`beta`, `stable`) + `latest` auto-track |
| **Namespace** | `@solocorp/x`, `@ceo/x`, `@security/x` — แยกตาม department |
| **Review** | Review flow + promotion request ก่อน publish สู่ global |
| **Governance** | Audit logs สำหรับทุก action — publish, download, delete |
| **RBAC** | Platform roles (SUPER_ADMIN, SKILL_ADMIN) + Namespace roles (OWNER, ADMIN, MEMBER) |
| **CLI** | `npx @astron-team/skillhub` — ติดตั้ง skill จาก registry โดยตรง |
| **Scanner** | Security scanner (Python/FastAPI) — ตรวจสอบ skill packages ก่อน publish |

### Tech Stack

| Component | เทคโนโลยี |
|:----------|:----------|
| Backend | Java 21, Spring Boot 3.2.3, Maven (7 modules) |
| Frontend | React 19, TypeScript, Vite, Radix UI, TanStack Query |
| Database | PostgreSQL 16 (Flyway migrations) |
| Cache | Redis 7 |
| Storage | LocalFS (dev) / S3/MinIO (prod) |
| Scanner | Python FastAPI, port 8000 |
| Build | `make dev-all` — full stack local |

---

## 2. Why SoloCorp Needs This

### ปัญหาที่ SkillHub แก้

| ก่อน SkillHub | หลัง SkillHub |
|:--------------|:--------------|
| Skill กระจายอยู่ตาม Face / Line / ไฟล์ในเครื่อง | Skill อยู่รวมใน Registry เดียว — ค้นหาได้, version ได้ |
| ไม่รู้ version ไหนล่าสุด | Semantic versioning + `latest` tag |
| ไม่รู้ skill ไหนใช้ได้/ไม่ได้ | Review flow + governance + audit log |
| แชร์ยาก — ต้องบอกกันปากต่อปาก | CLI install: `skillhub install @solocorp/mcp-scan` |
| ไม่มี access control — ใครก็แก้ได้ | RBAC + Namespace — แยกตาม department |

### SoloCorp Use Cases

1. **Skill packages สำหรับ AI Agents** — SOUL.md + tools + prompts
2. **MCP tool definitions** — แชร์ tools ข้าม department
3. **Security scan rules** — Red Team playbooks, HackAgent configs
4. **Pipeline templates** — Reusable pipeline definitions
5. **Content templates** — CMO reusable campaign templates

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                   SkillHub Registry              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Web UI   │  │ REST API │  │ Security     │  │
│  │ (React)  │  │ (Java)   │  │ Scanner      │  │
│  │ :3000    │  │ :8080    │  │ (Python)     │  │
│  └────┬─────┘  └────┬─────┘  │ :8000        │  │
│       │              │       └──────────────┘  │
│       └──────┬───────┘                         │
│              │                                 │
│  ┌───────────┴───────────┐                     │
│  │      PostgreSQL       │                     │
│  │      + Redis          │                     │
│  └───────────────────────┘                     │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              SoloCorp Ecosystem                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ MCP      │  │ Central  │  │ OpenCode     │  │
│  │ Server   │  │ Bus      │  │ Agents       │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Pipeline │  │ Loop     │  │ All 18 Dept  │  │
│  │ Runner   │  │ Runner   │  │ (Publish)    │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘
```

### Ports

| Service | Port |
|:--------|:----:|
| SkillHub Web UI | 3000 |
| SkillHub API | 8080 |
| SkillHub Scanner | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| MinIO (S3 compat) | 9000 |

---

## 4. Namespaces สำหรับ SoloCorp

### Proposed Namespace Structure

| Namespace | Owner | Description |
|:----------|:------|:------------|
| `@solocorp/global` | `SUPER_ADMIN` | Official SoloCorp skills — ทุก department publish ได้, ต้องผ่าน review |
| `@solocorp/ceo` | CEO Team | CEO tools, strategy templates |
| `@solocorp/security` | Cyber Security | Red Team playbooks, HackAgent configs, scan rules |
| `@solocorp/engineering` | Engineering | MCP tools, code templates, CI/CD pipelines |
| `@solocorp/architect` | Architect | Central Bus configs, routing rules, pipeline templates |
| `@solocorp/orchestrator` | Orchestrator | Workflow definitions, handoff templates |
| `@solocorp/marketing` | CMO | Campaign templates, content frameworks |
| `@solocorp/product` | Product | PRD templates, roadmap frameworks |
| `@solocorp/design` | Design | Design system components, UX patterns |
| `@solocorp/legal` | Legal | Contract templates, compliance checkers |
| `@solocorp/web3` | Web3 | Smart contract templates, Solana tools |

### Policy per Namespace

| Namespace | Visibility | Review Required | Max Versions |
|:----------|:----------:|:---------------:|:------------:|
| `@solocorp/global` | Public | ✅ Yes | Unlimited |
| `@solocorp/ceo` | Private | ✅ Yes | 50 |
| `@solocorp/security` | Restricted | ✅ Yes | 100 |
| `@solocorp/engineering` | Internal | ❌ No (Admin auto-approve) | 200 |
| `@solocorp/architect` | Internal | ❌ No (Admin auto-approve) | 100 |
| อื่นๆ | Internal | ❌ No | 50 |

---

## 5. Running SkillHub

### Prerequisites

- Docker & Docker Compose
- Java 21 (for local dev without Docker backend)
- Node.js 20+ (for frontend dev)
- pnpm (for frontend)

### Production Setup (แนะนำสำหรับ SoloCorp)

```bash
# 1. Clone
git clone https://github.com/Dr-SoloDev/skillhub.git
cd skillhub

# 2. Set environment
cp .env.release.example .env.release
# แก้ไข .env.release:
#   PUBLIC_URL=http://skillhub.solocorp.local:3000
#   DB_PASSWORD=...
#   STORAGE_TYPE=s3  # หรือ local

# 3. Start full stack
curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up --public-url http://skillhub.solocorp.local:3000

# หรือใช้ compose.release.yml โดยตรง
docker compose -f compose.release.yml up -d
```

### Development Setup

```bash
# Full stack local dev
make dev-all

# Access:
# - Web UI: http://localhost:3000
# - API: http://localhost:8080
# - Scanner: http://localhost:8000

# Mock users for testing:
# - X-Mock-User-Id: local-user  (regular user)
# - X-Mock-User-Id: local-admin  (super admin)
```

### Bootstrap Admin

| Username | Password | Role |
|:---------|:---------|:-----|
| `admin` | `ChangeMe!2026` | SUPER_ADMIN |

> ⚠️ **Security**: เปลี่ยน password และ disable BOOTSTRAP_ADMIN_ENABLED ทันทีหลัง setup เสร็จ

---

## 6. CLI Usage

### Install CLI

```bash
npm install -g @astron-team/skillhub

# หรือใช้ npx
npx @astron-team/skillhub@latest version
```

### Login

```bash
skillhub login --registry http://skillhub.solocorp.local:3000
```

### Publish Skill

```bash
# จาก directory ที่มี SKILL.md
skillhub publish --namespace @solocorp/security --name mcp-auth-validator --version 1.0.0
```

### Install Skill

```bash
skillhub install @solocorp/security/mcp-auth-validator
```

### Search

```bash
skillhub search --query "prompt injection"
skillhub search --namespace @solocorp/engineering
```

### Manage

```bash
# List installed
skillhub list

# Update
skillhub update @solocorp/security/mcp-auth-validator

# Yank (remove version)
skillhub yank @solocorp/security/mcp-auth-validator --version 1.0.0
```

---

## 7. Integration Points

### 7.1 SoloCorp MCP Server

เพิ่ม SkillHub tools ใน MCP Server:

```python
# solocorp_mcp/server.py (ในอนาคต)
@mcp.tool()
async def skillhub_search(query: str, namespace: str = None) -> str:
    """Search SkillHub registry for agent skills"""
    ...

@mcp.tool()
async def skillhub_install(skill_path: str) -> str:
    """Install a skill from SkillHub registry"""
    ...
```

### 7.2 Central Bus Integration

```
Pipeline Event → SkillHub Hook
┌──────────┐     ┌──────────┐
│ Pipeline │────▶│ SkillHub │
│ Complete │     │ Publish  │
└──────────┘     │ Artifact │
                 └──────────┘
```

### 7.3 Pipeline Integration

```yaml
# pipeline-config.yaml (อนาคต)
after_build:
  - action: skillhub_publish
    namespace: "@solocorp/engineering"
    version: "$VERSION"
    auto_approve: true  # สำหรับ engineering namespace
```

### 7.4 Red Team Integration

```bash
# Publish Red Team campaign artifacts
skillhub publish \
  --namespace @solocorp/security \
  --name red-team-campaign-q3-2026 \
  --version 1.0.0 \
  --tag beta
```

---

## 8. Skill Lifecycle Policy

### SoloCorp Custom Policy

```
DRAFT ──▶ SCANNING ──▶ UPLOADED ──▶ PENDING_REVIEW ──▶ PUBLISHED
             │                                              │
             ▼                                              ▼
        SCAN_FAILED                                     (future version)
             │                                              │
             ▼                                              ▼
        (fix + resubmit)                               YANKED (rollback)
```

| Stage | ใครทำได้ | Action |
|:------|:---------|:-------|
| **DRAFT** | OWNER/ADMIN | สร้าง skill package |
| **SCANNING** | ระบบ | Security scan อัตโนมัติ |
| **UPLOADED** | OWNER/MEMBER | Submit for review |
| **PENDING_REVIEW** | Namespace ADMIN | ตรวจสอบและ approve/reject |
| **PUBLISHED** | ระบบ | พร้อมใช้งาน — ทุกคน search & install ได้ |
| **YANKED** | SUPER_ADMIN | ถอน version ที่มีปัญหา |

### SLA

| Action | SLA |
|:-------|:---:|
| Security scan | < 30 วินาที |
| Review (engineering namespace) | < 1 ชั่วโมง |
| Review (global namespace) | < 24 ชั่วโมง |
| Vulnerability fix | ตาม severity (CRITICAL < 24 ชม.) |

---

## 9. Security & Access Control

### Roles

| Platform Role | สิทธิ์ |
|:--------------|:-------|
| `SUPER_ADMIN` | Full access — ทุก namespace, ทุก action |
| `SKILL_ADMIN` | จัดการ skill ทุกรายการ, ดู audit log |
| `USER_ADMIN` | จัดการผู้ใช้ |
| `AUDITOR` | Read-only — audit log + reports |

| Namespace Role | สิทธิ์ |
|:---------------|:-------|
| `OWNER` | Full control — members, settings, delete |
| `ADMIN` | Review, approve, publish, manage skills |
| `MEMBER` | Upload, update own skills |

### SoloCorp Initial Setup

| Namespace | Owner | Initial Members |
|:----------|:------|:----------------|
| `@solocorp/global` | `@ceo-hanuman` | All department heads (MEMBER) |
| `@solocorp/security` | `@cybersec-sai` | Red Team Operator, Threat Analyst |
| `@solocorp/engineering` | `@changful` | Engineering team members |

---

## Appendix — Useful Commands

```bash
# Dev
make dev-all              # Start full stack
make dev-all-down         # Stop
make dev-all-reset        # Reset data volumes
make dev-status           # Check services

# Test
make test-backend-app     # Backend tests
make test-frontend        # Frontend tests
make staging              # Full staging regression

# Smoke tests
./scripts/smoke-test.sh
./scripts/namespace-smoke-test.sh
./scripts/governance-smoke-test.sh
./scripts/promotion-smoke-test.sh

# CLI
npm install -g @astron-team/skillhub
skillhub --help
```

---

## References

- **GitHub**: https://github.com/Dr-SoloDev/skillhub
- **Docs**: https://iflytek.github.io/skillhub/
- **DeepWiki**: https://deepwiki.com/iflytek/skillhub
- **AGENTS.md**: `reference/skillhub/AGENTS.md`
- **Official README**: `reference/skillhub/README.md`

---

*SoloCorp OS — System First, Everything Follows*  
*SkillHub Integration v1.0 — ภายใต้การดูแลของ @architect-songsak*
