# ADR 001: Skill validation tooling and CI

**Status:** Accepted  
**Date:** 2026-03-26  
**Original context:** [GitHub issue #32](https://github.com/pkuppens/pkuppens/issues/32) — parent [issue #26](https://github.com/pkuppens/pkuppens/issues/26) (Skilz as install mechanism, deferred). **Canonical copy for this repo:** validation applies to [`pkuppens/skills`](https://github.com/pkuppens/skills).

## Context

This repository maintains a unified library of Agent Skills under `skills/`. Each skill is a directory containing `SKILL.md` with YAML frontmatter. Consumers link `skills/` into Cursor (`.cursor/skills/`), Claude (`.claude/skills/`), or Codex (`~/.codex/skills/`) per the [repository README](../../README.md).

**Canonical format** for portable skills is the [Agent Skills specification](https://agentskills.io/specification): required `name` and `description`, optional fields, and rules such as `name` matching the parent directory and character/length limits. Authoring conventions also live in [skills/CLAUDE.md](../../skills/CLAUDE.md) and [Claude — Agent Skills best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices#skill-structure).

**Skilz** ([SpillwaveSolutions/skilz-cli](https://github.com/SpillwaveSolutions/skilz-cli), PyPI package `skilz`, `pip install skilz`) is a **skill package manager** that installs skills into agent-specific locations. Its README states alignment with [agentskills.io](https://agentskills.io/) and the [AGENTS.md](https://agents.md/) ecosystem. It is **not** the definition of schema correctness for this repo: the spec is. Skilz remains an **optional** way for end users to install skills.

**Validation options considered:**

| Option | Pros | Cons |
|--------|------|------|
| **npm `skills-ref`** (pinned), `skills-ref validate <skill-dir>` | Referenced from the [specification page](https://agentskills.io/specification) as the reference validator; checks frontmatter against the spec. | The [npm package](https://www.npmjs.com/package/skills-ref) states it is for **demonstration purposes** and not production — acceptable for a lightweight Markdown repo CI if we treat it as “best available spec-aligned checker” and revisit if the upstream stance changes. |
| **Skilz CLI** | Same ecosystem as a future install story. | Not documented as a dedicated bulk `SKILL.md` linter in the upstream README; primary focus is install/list/search. |
| **Custom script** (e.g. Python + PyYAML) | Full control, no npm disclaimer. | Duplicates spec rules; maintenance burden when the spec evolves. |

## Decision

1. **Source of truth** for machine-checkable skill metadata remains **[agentskills.io](https://agentskills.io/specification)**.
2. **CI** runs **`skills-ref`** (global npm install, **version pinned** in [.github/workflows/validate-skills.yml](../../.github/workflows/validate-skills.yml)) against **each** directory under `skills/` that contains `SKILL.md`, and a pinned **`npx skills add <repo> --list -y`** smoke so the Skills CLI can still discover the tree (installer check, not schema validation).
3. **Skilz** is documented here as an **optional installer** for consumers, not as the validator for this repository.
4. **Revisit** this ADR if: `skills-ref` gains a production-ready designation, Skilz ships a first-class validate command we prefer, or we adopt a different official validator from the agentskills project.

## Skills CLI (`npx skills`)

The [Skills CLI](https://github.com/vercel-labs/skills) installs spec-shaped skills from Git into agent directories. It is **not** a schema validator: **CI still uses `skills-ref`** for frontmatter. A pinned `npx skills add <this-repo> --list` smoke test in GitHub Actions only proves the repository layout stays discoverable by the installer documented in the [repository README](../../README.md). Listing on [skills.sh](https://www.skills.sh/) remains optional marketing, not a merge gate.

## Consequences

- Pull requests that change files under `skills/` trigger validation; unrelated edits stay quiet (path filter on the workflow).
- Contributors see failures in GitHub Actions instead of only when loading a skill in an IDE.
- If `skills-ref` drifts from the spec or becomes unmaintained, swap the workflow step and update this ADR.

## Cursor and Claude

Both load `SKILL.md` from configured skill directories. **Spec-compliant** frontmatter is the shared baseline for interoperability. IDE-specific behaviour beyond the spec is out of scope for this ADR.
