"""
AI Software Factory — Orchestrator
===================================
Supervisor + swarm pattern using the Claude Agent SDK.
Confidential tasks → local Ollama via LiteLLM.
Public tasks       → Anthropic cloud.

Usage:
    python orchestrator.py "Fix the null pointer in auth/session.py"
    python orchestrator.py --confidential "Refactor billing/engine.py"
    python orchestrator.py --agent cloud-reviewer "Review the auth module"

Prerequisites:
    pip install claude-agent-sdk
    export ANTHROPIC_API_KEY=sk-ant-...
    export LITELLM_BASE_URL=http://localhost:4000   # from setup/litellm-gateway.md
    export LITELLM_API_KEY=sk-local-dev
"""

import asyncio
import argparse
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
LITELLM_BASE_URL  = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_API_KEY   = os.environ.get("LITELLM_API_KEY", "sk-local-dev")

# Model aliases — change these to pin different versions
CLOUD_FAST_MODEL  = "claude-haiku-4-5"      # cheap, fast — test running etc.
CLOUD_MAIN_MODEL  = "claude-sonnet-5"       # default supervisor + most cloud agents
LOCAL_CODE_MODEL  = "ollama/qwen2.5-coder:14b"  # local Ollama via LiteLLM

# ---------------------------------------------------------------------------
# Agent catalog
# ---------------------------------------------------------------------------
# Each entry maps to a .claude/agents/*.md file AND can be used programmatically.
# The `model` field overrides the default per-agent.
# Local agents get their own env block set at invocation time (see run_agent()).

AGENT_CATALOG: dict[str, AgentDefinition] = {

    "cloud-architect": AgentDefinition(
        description=(
            "High-level design and task decomposition. Use to break a complex feature "
            "into subtasks and identify which are LOCAL vs CLOUD. Output is a structured plan."
        ),
        prompt=open(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-architect.md")
        ).read() if os.path.exists(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-architect.md")
        ) else "You are a senior software architect. Decompose tasks and produce structured plans.",
        tools=["Read", "Glob", "Grep", "WebSearch"],
        model=CLOUD_MAIN_MODEL,
    ),

    "local-implementer": AgentDefinition(
        description=(
            "Small bug fixes, boilerplate, and refactors on confidential/proprietary code. "
            "Routes to local Ollama — no data leaves the machine. Use for changes under ~100 lines."
        ),
        prompt=open(
            os.path.join(os.path.dirname(__file__), "../agents/local-implementer.md")
        ).read() if os.path.exists(
            os.path.join(os.path.dirname(__file__), "../agents/local-implementer.md")
        ) else "You are a focused code implementation specialist. Make minimal, correct changes.",
        tools=["Read", "Edit", "Write", "Grep", "Glob"],
        model=LOCAL_CODE_MODEL,
    ),

    "cloud-reviewer": AgentDefinition(
        description=(
            "Code review for quality, correctness, and maintainability. Use after implementation "
            "agents have made changes. Returns structured review with blocking vs non-blocking issues."
        ),
        prompt=open(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-reviewer.md")
        ).read() if os.path.exists(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-reviewer.md")
        ) else "You are a senior code reviewer. Review for correctness and quality.",
        tools=["Read", "Grep", "Glob"],
        model=CLOUD_MAIN_MODEL,
    ),

    "cloud-security-scanner": AgentDefinition(
        description=(
            "Security vulnerability analysis. Use before merging or deploying. "
            "Scans for OWASP Top 10, injection flaws, secrets in code, and broken auth."
        ),
        prompt=open(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-security-scanner.md")
        ).read() if os.path.exists(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-security-scanner.md")
        ) else "You are an application security specialist. Find and report vulnerabilities.",
        tools=["Read", "Grep", "Glob"],
        model=CLOUD_MAIN_MODEL,
    ),

    "cloud-test-runner": AgentDefinition(
        description=(
            "Test execution and failure analysis. Use after implementation to verify correctness. "
            "Runs tests, parses failures, and suggests (but does not apply) fixes."
        ),
        prompt=open(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-test-runner.md")
        ).read() if os.path.exists(
            os.path.join(os.path.dirname(__file__), "../agents/cloud-test-runner.md")
        ) else "You are a test execution specialist. Run tests and report failures clearly.",
        tools=["Bash", "Read", "Grep"],
        model=CLOUD_FAST_MODEL,
    ),
}

# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def classify_task(prompt: str, confidential: bool) -> str:
    """Return the name of the agent best suited for the task."""
    if confidential:
        return "local-implementer"

    prompt_lower = prompt.lower()

    # Explicit agent keywords in the prompt
    if any(w in prompt_lower for w in ["security", "vulnerability", "cve", "owasp", "injection"]):
        return "cloud-security-scanner"
    if any(w in prompt_lower for w in ["review", "audit", "check style", "code quality"]):
        return "cloud-reviewer"
    if any(w in prompt_lower for w in ["test", "pytest", "unittest", "jest", "failing test"]):
        return "cloud-test-runner"
    if any(w in prompt_lower for w in ["design", "architecture", "plan", "decompose", "spec"]):
        return "cloud-architect"

    # Default: small implementation tasks go local for safety
    return "local-implementer"


def is_local_agent(agent_name: str) -> bool:
    return agent_name == "local-implementer"


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

async def run_agent(agent_name: str, prompt: str) -> str:
    """Run a single named agent and return its result."""
    agent_def = AGENT_CATALOG[agent_name]
    local = is_local_agent(agent_name)

    # For local agents, temporarily point the SDK at LiteLLM
    original_base_url = os.environ.get("ANTHROPIC_BASE_URL")
    original_api_key  = os.environ.get("ANTHROPIC_API_KEY")

    if local:
        os.environ["ANTHROPIC_BASE_URL"] = LITELLM_BASE_URL
        os.environ["ANTHROPIC_API_KEY"]  = LITELLM_API_KEY
    else:
        os.environ.pop("ANTHROPIC_BASE_URL", None)
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

    result = ""
    try:
        async for msg in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                # Forward the agent's persona and model to the SDK. Without
                # system_prompt and model here, the AgentDefinition's prompt and
                # model are silently dropped and every agent runs generic on the
                # default model — including the local Ollama routing, which
                # depends on model being the ollama/* name LiteLLM maps.
                system_prompt=agent_def.prompt,
                model=agent_def.model,
                allowed_tools=agent_def.tools or [],
            ),
        ):
            if hasattr(msg, "result") and msg.result:
                result = msg.result
    finally:
        # Restore environment
        if original_base_url is not None:
            os.environ["ANTHROPIC_BASE_URL"] = original_base_url
        else:
            os.environ.pop("ANTHROPIC_BASE_URL", None)
        os.environ["ANTHROPIC_API_KEY"] = original_api_key or ""

    return result


async def run_supervisor(user_prompt: str, confidential: bool, explicit_agent: str | None) -> None:
    """
    Supervisor loop.
    1. Optionally plan the task with the architect agent.
    2. Route to the appropriate worker agent.
    3. Optionally run review + test.
    """
    print(f"\n{'='*60}")
    print(f"  AI Software Factory")
    print(f"  Task: {user_prompt[:80]}{'...' if len(user_prompt) > 80 else ''}")
    print(f"  Confidential: {confidential}")
    print(f"{'='*60}\n")

    # --- Step 1: Route ---
    agent_name = explicit_agent or classify_task(user_prompt, confidential)
    print(f"[supervisor] Routing to: {agent_name}\n")

    # --- Step 2: Execute ---
    result = await run_agent(agent_name, user_prompt)
    print(f"[{agent_name}]\n{result}\n")

    # --- Step 3: Post-implementation pipeline (cloud tasks only) ---
    if not confidential and agent_name in ("local-implementer", "cloud-architect"):
        # Skip review/test for architect (it produces a plan, not code)
        if agent_name == "local-implementer":
            print("[supervisor] Running post-implementation review...\n")
            review = await run_agent(
                "cloud-reviewer",
                f"Review the changes just made for this task: {user_prompt}\n"
                f"Implementation summary:\n{result}"
            )
            print(f"[cloud-reviewer]\n{review}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI Software Factory orchestrator"
    )
    parser.add_argument("prompt", help="Task description")
    parser.add_argument(
        "--confidential", "-c",
        action="store_true",
        help="Force routing to local Ollama agent (no data sent to cloud)"
    )
    parser.add_argument(
        "--agent", "-a",
        choices=list(AGENT_CATALOG.keys()),
        default=None,
        help="Override automatic routing and use a specific agent"
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List available agents and exit"
    )
    args = parser.parse_args()

    if args.list_agents:
        print("\nAvailable agents:\n")
        for name, agent in AGENT_CATALOG.items():
            locality = "LOCAL (Ollama)" if is_local_agent(name) else "CLOUD (Anthropic)"
            print(f"  {name:30s} [{locality}]")
            print(f"    {agent.description[:80]}...")
            print()
        sys.exit(0)

    asyncio.run(run_supervisor(args.prompt, args.confidential, args.agent))


if __name__ == "__main__":
    main()
