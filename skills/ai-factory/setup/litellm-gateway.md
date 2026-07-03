# LiteLLM Gateway Setup — Ollama Bridge

Bridges Claude Code and the Agent SDK to your local Ollama instance via an Anthropic-compatible API.

> **Warning:** LiteLLM PyPI v1.82.7 and v1.82.8 were compromised with credential-stealing malware.  
> Always verify you're installing a safe version: `pip install 'litellm>=1.82.9'`

---

## Prerequisites

- Ollama installed and running: `ollama serve`
- At least one coding model pulled (see `ollama-models.md`)
- Python 3.10+

---

## Step 1 — Install LiteLLM

```bash
pip install 'litellm[proxy]>=1.82.9'
```

---

## Step 2 — Create `litellm_config.yaml`

Place this in your project root or a shared config location (e.g. `~/.config/litellm/config.yaml`):

```yaml
model_list:
  # Local Ollama models
  - model_name: ollama/qwen2.5-coder:14b
    litellm_params:
      model: ollama/qwen2.5-coder:14b
      api_base: http://localhost:11434

  - model_name: ollama/llama3.1:8b
    litellm_params:
      model: ollama/llama3.1:8b
      api_base: http://localhost:11434

  # Passthrough to Anthropic for cloud agents
  # (cloud agents bypass this gateway and use ANTHROPIC_API_KEY directly)

litellm_settings:
  # Return Anthropic-compatible response format
  drop_params: true
  set_verbose: false

general_settings:
  master_key: "sk-local-dev"   # Change this for non-dev environments
```

---

## Step 3 — Start the gateway

```bash
litellm --config litellm_config.yaml --port 4000
```

Verify it's running:
```bash
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer sk-local-dev" | python -m json.tool
```

You should see your Ollama models listed.

---

## Step 4 — Configure environment variables

For the local agents, set these in your shell or in `.env`:

```bash
# Used by local-implementer agent and orchestrator.py for local routing
export LITELLM_BASE_URL="http://localhost:4000"
export LITELLM_API_KEY="sk-local-dev"

# Used by cloud agents (unchanged — direct Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."
```

The `orchestrator.py` template reads these and sets `ANTHROPIC_BASE_URL` only for agents that should run locally.

---

## Step 5 — Verify end-to-end

```bash
python - <<'EOF'
import asyncio, os
os.environ["ANTHROPIC_BASE_URL"] = "http://localhost:4000"
os.environ["ANTHROPIC_API_KEY"] = os.environ["LITELLM_API_KEY"]
from claude_agent_sdk import query, ClaudeAgentOptions

async def test():
    async for msg in query(
        prompt="Say 'gateway OK' and nothing else.",
        options=ClaudeAgentOptions(
            allowed_tools=[],
            model="ollama/qwen2.5-coder:14b"
        ),
    ):
        if hasattr(msg, "result"):
            print("Local gateway response:", msg.result)

asyncio.run(test())
EOF
```

---

## Running as a background service (optional)

**systemd (Linux):**
```ini
# /etc/systemd/system/litellm.service
[Unit]
Description=LiteLLM Proxy
After=network.target

[Service]
ExecStart=/usr/local/bin/litellm --config /etc/litellm/config.yaml --port 4000
Restart=on-failure
Environment=HOME=/root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable litellm && sudo systemctl start litellm
```

**Windows (Task Scheduler or as a background process):**
```powershell
Start-Process -NoNewWindow -FilePath "litellm" `
  -ArgumentList "--config", "$HOME\.config\litellm\config.yaml", "--port", "4000"
```

---

## Security notes

- `master_key` is the API key your agents use to authenticate with LiteLLM.
- LiteLLM runs on `localhost` — it is not exposed externally in this setup.
- Never commit `litellm_config.yaml` with real credentials. Use environment variable references (`os.environ/SOME_KEY`) in the config for production.
- For team deployments, run LiteLLM on a shared server behind your corporate network and replace `localhost:4000` with that server's address.
