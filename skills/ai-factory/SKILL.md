# AI Software Factory — Supervisor + Swarm

**Invoke:** `/ai-factory`  
**Use when:** setting up, running, or troubleshooting multi-agent workflows where some tasks must stay on-premises (confidential data, proprietary code) and others can run on cloud Claude.

---

## Architecture

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│  SUPERVISOR (Claude Sonnet — cloud)     │
│  • Decomposes task                      │
│  • Classifies subtasks by sensitivity   │
│  • Orchestrates sub-agents              │
│  • Merges results                       │
└───────┬─────────────────┬───────────────┘
        │                 │
        ▼                 ▼
┌───────────────┐  ┌──────────────────────┐
│ CLOUD AGENTS  │  │  LOCAL AGENTS         │
│ (Anthropic)   │  │  (Ollama via LiteLLM) │
│               │  │                       │
│ • architect   │  │ • local-implementer   │
│ • reviewer    │  │   (small bugs, boiler-│
│ • security    │  │    plate, refactors)  │
│ • test-runner │  │                       │
└───────────────┘  └──────────────────────┘
```

## Routing Rules

| Task type | Confidential? | Agent | Model |
|-----------|--------------|-------|-------|
| Architecture / design | No | `cloud-architect` | claude-sonnet-4-6 |
| Small bug fix / impl | **Yes** | `local-implementer` | ollama/qwen2.5-coder:14b |
| Boilerplate / scaffold | **Yes** | `local-implementer` | ollama/qwen2.5-coder:14b |
| Code review | No | `cloud-reviewer` | claude-sonnet-4-6 |
| Security scan | No | `cloud-security-scanner` | claude-sonnet-4-6 |
| Test execution | No | `cloud-test-runner` | claude-haiku-4-5 |

**Rule of thumb:** if the file contains proprietary business logic, PII, credentials, or trade secrets → route to a local agent. Everything else can go to the cloud.

---

## Quick Start

### 1. Set up LiteLLM gateway
See `setup/litellm-gateway.md` — installs in ~5 minutes with Ollama already running.

### 2. Deploy agent definitions
Copy the files from `agents/` into your project's `.claude/agents/` directory:
```bash
cp skills/ai-factory/agents/*.md .claude/agents/
```
These are picked up automatically by Claude Code CLI and the Agent SDK at startup.

### 3. Run the orchestrator
```bash
cd your-project
python skills/ai-factory/templates/orchestrator.py "Fix the null pointer in auth/session.py"
```

Or for a confidential task (forces local routing):
```bash
python skills/ai-factory/templates/orchestrator.py \
  --confidential \
  "Refactor the billing calculation logic in billing/engine.py"
```

### 4. Use from Claude Code CLI
With agents copied to `.claude/agents/`, you can invoke them directly:
```
/local-implementer Fix the off-by-one in src/parser.py line 42
/cloud-reviewer Review the changes in the auth module for security issues
```

---

## Files in this Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — architecture and usage guide |
| `setup/litellm-gateway.md` | LiteLLM + Ollama bridge setup |
| `setup/ollama-models.md` | Recommended local models per use case |
| `agents/cloud-architect.md` | Agent def: high-level planning (cloud) |
| `agents/cloud-reviewer.md` | Agent def: code review (cloud) |
| `agents/cloud-security-scanner.md` | Agent def: security analysis (cloud) |
| `agents/cloud-test-runner.md` | Agent def: test execution (cloud) |
| `agents/local-implementer.md` | Agent def: small fixes and boilerplate (local Ollama) |
| `templates/orchestrator.py` | Python Agent SDK orchestrator with routing logic |

---

## Key Concepts

**Sub-agents run in isolated context windows.** The supervisor only sees their final result — not every file they read. This keeps the main context lean and costs low.

**Pre-defined agents = predictable behavior.** Each agent has a fixed system prompt, tool set, and model. The supervisor can't accidentally give a local agent internet access, or route confidential data to a cloud model.

**LiteLLM is the routing layer.** It exposes an Anthropic-compatible API endpoint. The `local-implementer` agent points its `ANTHROPIC_BASE_URL` at LiteLLM, which forwards to Ollama. Cloud agents use `ANTHROPIC_API_KEY` directly. The supervisor never changes — only the gateway config differs.

**Skills stay in your repo.** Check `agents/*.md` into source control alongside your `CLAUDE.md`. Every developer on the team gets the same agent behavior automatically.
