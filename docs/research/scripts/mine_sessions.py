"""Mine local Claude Code transcripts for friction signals (issue #43, R1).

Reads ~/.claude/projects/**/*.jsonl and prints aggregate counts (no transcript text)
to stdout. With --examples PATH it also writes raw snippets for manual reading; keep
that file under the gitignored tmp/, because raw transcript content must never be
committed (ADR 003).

Usage: python -I docs/research/scripts/mine_sessions.py [--examples tmp/skills/session-learning/examples.json]
"""

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"

CORRECTION = re.compile(
    r"^\s*(no\b|nope|nee\b|don'?t\b|do not\b|stop\b|wrong\b|that'?s not|not what|i said|"
    r"why did you|why do you|instead\b|actually\b|undo\b|revert\b|niet\b)",
    re.IGNORECASE,
)
CORRECTION_ANY = re.compile(
    r"\b(you forgot|you missed|you didn'?t|still (broken|failing|wrong)|again\?|i told you|"
    r"as i said|not (correct|right)|that is wrong|doesn'?t work|didn'?t work)\b",
    re.IGNORECASE,
)


def error_class(text: str) -> str:
    t = text.lower()
    rules = [
        (
            "permission-denied",
            ["doesn't want to proceed", "user rejected", "permission", "denied"],
        ),
        ("edit-not-read-first", ["has not been read yet", "read it first"]),
        (
            "edit-string-not-found",
            ["string to replace not found", "not found in file", "no match"],
        ),
        ("edit-not-unique", ["found multiple", "not unique", "matches of the string"]),
        (
            "file-not-found",
            ["no such file", "does not exist", "cannot find path", "file not found"],
        ),
        (
            "input-validation",
            ["inputvalidationerror", "invalid input", "validation error"],
        ),
        ("timeout", ["timed out", "timeout"]),
        (
            "shell-syntax",
            ["syntax error", "unexpected token", "parsererror", "is not recognized"],
        ),
        ("tool-unavailable", ["no such tool available"]),
        ("blocked-by-harness", ["blocked:", "command line is too long"]),
        ("auth", ["http 401", "http 403", "authenticate", "credential", "gh auth"]),
        ("network", ["could not resolve", "connection", "econn", "network"]),
        ("test-or-lint-failure", ["failed", "assert", "error:", "ruff", "pytest"]),
        ("nonzero-exit", ["exit code"]),
    ]
    for name, needles in rules:
        if any(n in t for n in needles):
            return name
    return "other"


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            b.get("text", "") if isinstance(b, dict) and b.get("type") == "text" else ""
            for b in content
        )
    return ""


def result_text(block) -> str:
    c = block.get("content")
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


TAG_BLOCK = re.compile(
    r"<(ide_[\w]+|system-reminder|local-command-[\w]+|command-[\w]+)>.*?</>", re.DOTALL
)


def strip_tags(text: str) -> str:
    return TAG_BLOCK.sub("", text).strip()


def is_human_prompt(rec, text: str) -> bool:
    if rec.get("isMeta") or rec.get("isCompactSummary") or rec.get("isSidechain"):
        return False
    s = strip_tags(text)
    if not s or s.startswith(("<", "Caveat:")):
        return False
    return "[Request interrupted" not in s


def main() -> None:
    files = sorted(ROOT.rglob("*.jsonl"))
    totals = collections.Counter()
    err_by_class = collections.Counter()
    err_by_tool = collections.Counter()
    skills = collections.Counter()
    slash = collections.Counter()
    per_project = collections.defaultdict(collections.Counter)
    repeated_fail_heads = collections.Counter()
    thrash_files = 0
    examples = collections.defaultdict(list)

    for f in files:
        project = f.relative_to(ROOT).parts[0]
        totals["sessions"] += 1
        tool_names: dict[str, tuple[str, dict]] = {}
        fail_cmds = collections.Counter()
        edits = collections.Counter()
        for line in f.open(encoding="utf-8", errors="replace"):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            typ = rec.get("type")
            if typ == "system" and rec.get("subtype") == "compact_boundary":
                totals["compactions"] += 1
                per_project[project]["compactions"] += 1
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if typ == "assistant" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        name, inp = b.get("name", "?"), b.get("input") or {}
                        tool_names[b.get("id")] = (name, inp)
                        totals["tool_calls"] += 1
                        per_project[project]["tool_calls"] += 1
                        if name == "Skill":
                            skills[inp.get("skill", "?")] += 1
                        if name in ("Edit", "Write", "MultiEdit"):
                            edits[inp.get("file_path", "?")] += 1
            if typ == "user":
                if isinstance(content, list):
                    for b in content:
                        if (
                            isinstance(b, dict)
                            and b.get("type") == "tool_result"
                            and b.get("is_error")
                        ):
                            name, inp = tool_names.get(b.get("tool_use_id"), ("?", {}))
                            txt = result_text(b)
                            cls = error_class(txt)
                            err_by_class[cls] += 1
                            err_by_tool[name] += 1
                            totals["tool_errors"] += 1
                            per_project[project]["tool_errors"] += 1
                            if len(examples[cls]) < 8:
                                examples[cls].append({"tool": name, "text": txt[:300]})
                            cmd = inp.get("command") if isinstance(inp, dict) else None
                            if cmd:
                                fail_cmds[cmd.strip()] += 1
                text = text_of(content)
                if "[Request interrupted by user" in text:
                    totals["interrupts"] += 1
                    per_project[project]["interrupts"] += 1
                for m in re.findall(r"<command-name>/?([\w:.-]+)</command-name>", text):
                    slash[m] += 1
                if is_human_prompt(rec, text):
                    totals["human_prompts"] += 1
                    per_project[project]["human_prompts"] += 1
                    clean = strip_tags(text)
                    if len(examples["prompt"]) < 400:
                        examples["prompt"].append(
                            {"project": project, "text": clean[:500]}
                        )
                    if CORRECTION.search(clean) or CORRECTION_ANY.search(clean):
                        totals["corrections"] += 1
                        per_project[project]["corrections"] += 1
                        if len(examples["correction"]) < 60:
                            examples["correction"].append(
                                {"project": project, "text": clean[:400]}
                            )
        for cmd, n in fail_cmds.items():
            if n >= 2:
                totals["repeated_failing_cmds"] += 1
                repeated_fail_heads[cmd.split()[0] if cmd.split() else "?"] += 1
        thrash_files += sum(1 for n in edits.values() if n >= 5)

    totals["files_edited_5plus_times"] = thrash_files
    report = {
        "totals": totals,
        "errors_by_class": err_by_class.most_common(),
        "errors_by_tool": err_by_tool.most_common(15),
        "repeated_failing_cmd_heads": repeated_fail_heads.most_common(15),
        "skill_invocations": skills.most_common(30),
        "slash_commands": slash.most_common(30),
        "per_project": {p: dict(c) for p, c in per_project.items()},
    }
    json.dump(report, sys.stdout, indent=1, default=dict)
    if "--examples" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--examples") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(examples, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
