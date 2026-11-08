# SoloCorp OS — Operations Runbook

> **Version:** 0.2.0  
> **Last Updated:** 2026-07-12  
> **Service:** Central Bus — Core Event Bus  
> **Port:** 8099 (default)

---

## Architecture Overview

SoloCorp OS is a multi-agent orchestration platform. The **Central Bus** (FastAPI
on port 8099) is the core event bus — it accepts governance artifacts, manages a
file-based priority queue at `bus/queue/`, and tracks project pipeline state in
`bus/projects/`. The **Agent Worker Service** polls the Central Bus queue,
routes messages to the appropriate agent (CFO, Architect, Engineering, Product,
QA, etc.), and reports results back. The **Loop Runner** (cron every 30 min)
executes recurring governance loops. The **MCP Server** exposes SoloCorp
capabilities to external coding agents via the Model Context Protocol.

```
                  ┌──────────────────────┐
                  │   External Agents     │
                  │  (OpenCode, Claude    │
                  │   Code, Codex, etc.)  │
                  └──────┬───────────────┘
                         │ MCP
                  ┌──────▼───────────────┐
                  │  solocorp_mcp.server │
                  └──────┬───────────────┘
                         │
                  ┌──────▼───────────────┐
                  │   Central Bus        │
                  │  (port 8099)         │
                  │  bus/queue/          │
                  └──────┬───────────────┘
                         │ poll
                  ┌──────▼───────────────┐
                  │  Agent Worker        │
                  │  (agent_worker_      │
                  │   service.py)        │
                  └──────┬───────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       CFO Agent   Architect    Engineering
       Product     QA           ...
                         
┌──────────────────────────────────────┐
│  Loop Runner (cron */30)             │
│  loop_runner.main                    │
└──────────────────────────────────────┘
```

---

> **Note:** `govctl` is a legacy/optional CLI. The primary services are Central Bus (port 8099), Agent Worker, Loop Runner, and MCP Server. See sections below for those.

## Commands Reference (Legacy)

### govctl CLI

| Command | Description |
|---------|-------------|
| `govctl validate adr` | Validate all ADRs |
| `govctl threshold assess <path>` | Complexity assessment of a TOML artifact |
| `govctl bridge start` | Start bridge daemon (watches `gov/` for changes) |
| `govctl bridge publish <path>` | Publish a single TOML artifact to Central Bus |
| `govctl bridge status` | Check bridge daemon status |
| `govctl bridge stop` | Stop bridge daemon |
| `govctl bridge ao-start` | Start AO bridge listener |
| `govctl bridge ao-stop` | Stop AO bridge listener |
| `govctl bridge ao-status` | Show AO bridge listener status |
| `govctl ao list` | List AO agents |
| `govctl ao run <agent>` | Run an AO agent (`ceo`, `orchestrator`, `architect`, `engineering`, `qa`) |
| `govctl ao status` | Show AO CLI and agent registry status |
| `govctl ao bridge <start\|stop\|status>` | Manage AO bridge daemon |
| `govctl api start` | Start FastAPI REST server (daemon, port 8765) |
| `govctl api stop` | Stop API server |
| `govctl api status` | Check API server status |
| `govctl dashboard` | Show one-shot terminal dashboard |
| `govctl dashboard --watch` | Live-updating terminal dashboard (refresh every 5s) |
| `govctl dashboard --watch --interval 2` | Live dashboard with 2s refresh |
| `govctl init` | Initialize governance directory structure in `gov/` |
| `govctl status` | Show governance artifact counts |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serve dashboard SPA (`index.html`) |
| GET | `/static/*` | Serve static assets (CSS, JS) |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/gov/adrs` | List ADRs |
| POST | `/api/v1/gov/adrs` | Create a new ADR |
| GET | `/api/v1/gov/rfcs` | List RFCs |
| GET | `/api/v1/gov/guards` | List Guards |
| GET | `/api/v1/agents` | List 5 AO agents |
| POST | `/api/v1/agents/{id}/run` | Run an agent (non-blocking) |
| GET | `/api/v1/pipeline/status` | Pipeline status for all projects |
| GET | `/api/v1/metrics` | System-wide metrics |

---

## Startup Sequence

### 1. Prepare environment

```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

### 2. Bootstrap CEO memory

```bash
bash scripts/bootstrap-ceo.sh
```

This copies `.env.example` → `.env` (if not present), initializes Central Bus
directories, restores CEO memory from `brain/ceo-memory.json`, and configures
MCP for all supported coding agents (OpenCode, Claude Code, Codex, Cursor).

### 3. Start all services

```bash
bash scripts/start-services.sh
```

This launches (in order):
| Service | Command | Log |
|---------|---------|-----|
| Central Bus | `uvicorn central_bus.main:app --host 127.0.0.1 --port 8099` | `/tmp/central_bus.log` |
| Agent Worker | `python3 -m workers.agent_worker_service` | `/tmp/agent_worker.log` |

### 4. (Optional) Start Loop Runner

The Loop Runner runs via cron every 30 minutes. To run it manually:

```bash
python3 -m loop_runner.main
```

To install the cron job:

```bash
crontab -l 2>/dev/null; echo "*/30 * * * * cd $(pwd) && python3 -m loop_runner.main >> /tmp/loop_runner.log 2>&1" | crontab -
```

### 5. (Optional) Start MCP Server

```bash
python3 -m solocorp_mcp.server
```

The MCP server is also auto-configured in `opencode.json` and
`.claude/settings.json` by `bootstrap-ceo.sh`.

### 6. Import routing rules (one-time)

Routing rules in `bus/system/routing_rules.json` must be imported into SQLite:

```bash
source .venv/bin/activate
python3 -c "
import json, sqlite3, uuid
db = sqlite3.connect('central_bus/bus.db')
rules = json.load(open('bus/system/routing_rules.json'))['rules']
route_map = {
    'cfo':'cfo-meetoo','cmo':'cmo-mark','architect':'architect-songsak',
    'product':'product-produck','engineering':'changful','design':'design-kreet',
    'ui_designer':'ui-designer','qa':'qa','sales':'sales','support':'support',
    'web3':'web3-aywa','legal':'legal-tulya','orchestrator':'orchestrator-wut',
    'ceo':'ceo-hanuman',
}
priority_map = {'critical':0,'high':1,'normal':2,'low':3}
db.execute('DELETE FROM routing_rules')
for r in rules:
    db.execute('INSERT INTO routing_rules (id,name,description,source_agent,target_department,condition,priority,enabled,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,datetime(\"now\"),datetime(\"now\"))',
        (str(uuid.uuid4()), r['rule_id'], 'Route '+str(r['trigger']['keywords'])+' to '+route_map.get(r['route_to'],r['route_to']), '*', route_map.get(r['route_to'],r['route_to']+'-unknown'), json.dumps({'keywords':r['trigger']['keywords']}), priority_map.get(r.get('priority','normal'),2), 1))
db.commit()
print('✅ Imported', len(rules), 'routing rules')
"
```

### 8. Verify services

```bash
# Central Bus health check
curl http://127.0.0.1:8099/health

# Check running processes
ps aux | grep -E 'central_bus|agent_worker|loop_runner|solocorp_mcp'

# View logs
tail -f /tmp/central_bus.log
tail -f /tmp/agent_worker.log
```

---

## Agent Worker Service

The Agent Worker Service polls Central Bus queue, routes messages to the
appropriate agent, and reports results back. It uses `workers/llm_provider.py`
for LLM inference and supports 15+ agents defined in `workers/agents/`.

### Start

```bash
python3 -m workers.agent_worker_service
```

Or as a background daemon (recommended with `-u` for unbuffered stdout):

```bash
nohup python3 -u -m workers.agent_worker_service > /tmp/agent_worker.log 2>&1 &
```

### Stop

```bash
pkill -f workers.agent_worker_service
```

### Status

```bash
ps aux | grep agent_worker_service

# View recent activity
tail -20 /tmp/agent_worker.log
```

### Logs

```
/tmp/agent_worker.log
```

---

## Loop Runner

The Loop Runner executes recurring governance loops (strategy review, market
scan, risk assessment, etc.) defined in `loop_runner/loops/`.

### Run manually

```bash
python3 -m loop_runner.main
```

### Cron schedule

Runs every 30 minutes. To set up:

```bash
crontab -l 2>/dev/null
echo "*/30 * * * * cd /path/to/repo && python3 -m loop_runner.main >> /tmp/loop_runner.log 2>&1" | crontab -
```

### Logs

```
/tmp/loop_runner.log
```

---

## MCP Server

Exposes SoloCorp capabilities (departments, routing, commands) to external
coding agents via Model Context Protocol.

### Start

```bash
python3 -m solocorp_mcp.server
```

### Configured by

`bootstrap-ceo.sh` writes MCP configs for:
- OpenCode: `opencode.json`
- Claude Code: `.claude/settings.json`
- Codex CLI: `.codex/config.toml`
- Cursor: `.cursor/mcp.json`

---

## Monitoring

### Central Bus Health Check

```bash
curl http://127.0.0.1:8099/health
# → {"status":"ok","service":"central-bus"}
```

### Queue Metrics

```bash
# Check queue file sizes
wc -l bus/queue/*.jsonl

# Inspect dead letters
python -c "
from central_bus.queue import list_dead_letters
for dl in list_dead_letters():
    print(dl['message']['id'], dl['reason'])
"
```

### Process Health

```bash
ps aux | grep -E 'central_bus|agent_worker|loop_runner|solocorp_mcp'
```

### Logs

```bash
# Central Bus
tail -f /tmp/central_bus.log

# Agent Worker
tail -f /tmp/agent_worker.log

# Loop Runner
tail -f /tmp/loop_runner.log
```

---

## Restart Procedure

Use this procedure to cleanly restart all services.

### 1. Stop all services

```bash
# Stop Agent Worker
pkill -f workers.agent_worker_service

# Stop Central Bus
pkill -f central_bus.main

# Stop Loop Runner (if running)
pkill -f loop_runner.main

# Stop MCP Server (if running)
pkill -f solocorp_mcp.server
```

### 2. Start all services

```bash
bash scripts/start-services.sh
```

### 3. Verify

```bash
# Central Bus health check
curl http://127.0.0.1:8099/health

# Check running processes
ps aux | grep -E 'central_bus|agent_worker|loop_runner|solocorp_mcp'
```

---

## Troubleshooting

### Central Bus won't start

```
Symptom:  "Port 8099 already in use"
Fix:      pkill -f central_bus.main
          # or kill manually:
          kill $(lsof -t -i:8099)
Restart:  bash scripts/start-services.sh

Symptom:  "uvicorn is not installed"
Fix:      pip install uvicorn[standard]
```

### Agent Worker won't start

```
Symptom:  Worker exits immediately
Fix 1:    Check Central Bus is running on port 8099
Fix 2:    Check logs:  tail -20 /tmp/agent_worker.log
Fix 3:    Verify .env has valid API keys for LLM provider
          (workers/llm_provider.py reads LLM_API_KEY from .env)

Symptom:  Queue poll failed: "No module named 'pydantic_settings'"
Fix:      pip install pydantic_settings  (add to central_bus/requirements.txt)

Symptom:  Worker starts but doesn't log poll results
Fix:      Use python -u flag for unbuffered output:
          nohup python3 -u -m workers.agent_worker_service > /tmp/agent_worker.log 2>&1 &

Symptom:  "TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'"
          (Central Bus fails to start or tests fail)
Fix:      Starlette v1.x removed on_startup param. Pin to <0.39.0:
          pip install "starlette>=0.37.2,<0.39.0"
```

### Loop Runner errors

```
Symptom:  "No module named loop_runner"
Fix:      Run from repo root:  python3 -m loop_runner.main
Confirm:  python3 -c "import loop_runner; print('OK')"
```

### MCP Server errors

```
Symptom:  Connection refused from coding agent
Fix 1:    Ensure server is running: python3 -m solocorp_mcp.server
Fix 2:    Check opencode.json or .claude/settings.json for correct path
Fix 3:    Re-run bootstrap:  bash scripts/bootstrap-ceo.sh
```

### Queue messages accumulating

Dead letters accumulate in `bus/queue/dead_letter/`. Inspect them:

```bash
python -c "
from central_bus.queue import list_dead_letters
for dl in list_dead_letters():
    print(dl['message']['id'], dl['reason'])
"
```

### Governance state corruption

If a project `state.json` becomes unreadable, inspect the file:

```bash
cat bus/projects/<project_id>/state.json | python -m json.tool
```

To recover, re-initialise the project state (this is destructive):

```bash
python -c "
from central_bus.state import init_project
init_project('<project_id>', name='Recovered Project')
"
```

---

## Data Layout

```
./
├── bus/
│   ├── governance/           # Guard event logs per project
│   │   └── <project_id>/
│   │       └── guard_events.jsonl
│   ├── projects/             # Pipeline state per project
│   │   └── <project_id>/
│   │       ├── state.json    # Current phase, status, blockers
│   │       └── audit/        # Immutable message audit log
│   │           └── YYYY-MM-DD.jsonl
│   └── queue/                # Message queue (priority-based JSONL)
│       ├── critical.jsonl
│       ├── high.jsonl
│       ├── normal.jsonl
│       ├── low.jsonl
│       └── dead_letter/      # Failed messages after max retries
├── brain/
│   ├── ceo-memory.json       # CEO persistent memory
│   └── session-log.md        # Session history
├── gov/
│   ├── adr/                  # Architecture Decision Records (TOML)
│   ├── rfc/                  # Request for Comments (TOML)
│   ├── guards/               # Verification Guards (TOML)
│   ├── config/               # govctl configuration
│   ├── config.toml           # System config
│   └── ao_config.toml        # Agent Orchestrator config
├── loop_runner/
│   ├── main.py               # Entry point (cron every 30min)
│   └── loops/                # Loop definitions
├── workers/
│   ├── agent_worker_service.py  # Central Bus queue consumer
│   ├── llm_provider.py          # LLM inference provider
│   └── agents/                  # Agent implementations
├── solocorp_mcp/
│   └── server.py             # MCP protocol server
├── scripts/
│   ├── bootstrap-ceo.sh      # First-time setup
│   └── start-services.sh     # Launch Central Bus + Agent Worker
└── logs/                     # Runtime logs
```
