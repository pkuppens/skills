---
name: skill-creation
description: >-
  Authors AI agent skills for Cursor, Claude Code, and similar tools using SKILL.md
  structure and progressive disclosure. Use when creating, writing, or refactoring a
  skill; when the user mentions SKILL.md, skill frontmatter, or skill best practices;
  or when the user invokes slash commands that map here (includes create-skill).
---

# Skill creation (canonical)

Guides authoring of reusable agent skills per [Claude skill best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices). Cursor’s bundled `create-skill` under `skills-cursor/` is reference-only; **this folder is authoritative** for the `pkuppens/skills` skill tree (`skills/`, linked into IDEs by symlink, Skills CLI or the Claude Code plugin marketplace — see the [repository README](../../../README.md)).

## When to read this skill

- New or rewritten skills, sub-skills, or meta-skills under `skills/`
- Questions about YAML frontmatter, description wording, layout, or token budget
- Ported workflows from Cursor-only docs into portable, Claude-aligned shape

Deep patterns, anti-patterns, phased workflow, checklists, and optional project-facing trim live in [reference.md](reference.md).

## Discovery (gather before drafting)

Infer from context where possible; otherwise confirm:

1. **Purpose / scope** — one capability per skill folder
2. **Location** — personal (`~/.cursor/skills/` or synced `skills/`) vs repo-local `.cursor/skills/` for team-only overlays
3. **Triggers** — when the agent should apply the skill automatically vs only when invoked
4. **Domain facts** — only what models do not reliably know already
5. **Output shapes** — templates, headings, or review formats required
6. **Precedent** — existing skills in this tree to mirror
7. **Public ecosystem (agent skills)** — before drafting, compare intent to published skills (browse [skills.sh](https://www.skills.sh/), run `npx skills find <query>`). The external `find-skills` skill ([vercel-labs/skills](https://github.com/vercel-labs/skills)) covers the commands. Record **reuse** (install or symlink if license and layout allow), **learn** (adapt ideas without copying), or **build** (no good fit). If personal or project rules differ from a public skill, note the delta; do not discard local requirements for the sake of alignment. Vendor stacks (e.g. Azure DevOps) often belong in **reuse-via-install**, not a new repo skill — see [reference.md](reference.md#example-platform-tooling-azure-devops). More detail: [reference.md](reference.md#public-agent-skills-ecosystem-before-authoring).

**Verbatim user copy:** If the user supplies exact wording for the skill body, place it **verbatim** in `SKILL.md` (same words, same order). Do not paraphrase or wrap with extra headings unless they asked.

**Clarification:** Prefer the AskQuestion tool when available; otherwise ask in chat (e.g. personal vs project path, whether to add `scripts/`).

## Directory layout

```text
skill-name/
├── SKILL.md          # required
├── reference.md      # optional (detail, patterns)
├── examples.md       # optional
└── scripts/          # optional (stable helpers; document run vs read)
```

**Do not** author new skills under `~/.cursor/skills-cursor/` (Cursor-managed). **Do** keep skills in this repo under `skills/<name>/` or in a project’s `.cursor/skills/<name>/` when the skill is repository-specific.

## YAML frontmatter

```yaml
---
name: skill-name
description: >-
  What the skill does in third person; include trigger terms and "Use when …".
  WHAT + WHEN; max 1024 chars.
---
```

| Field | Rule |
|-------|------|
| `name` | ≤64 chars; lowercase letters, digits, hyphens only |
| `description` | Non-empty; third person; concrete triggers (not "helps with X" only) |

Keep frontmatter compatible with `skills-ref`; do not add tool-specific invocation fields.

## Writing descriptions

Third person only. Prefer: *"Analyzes spreadsheets and suggests pivots. Use when working with `.xlsx` or tabular exports."*

Avoid vague one-liners and first/second person ("I", "you can").

Further examples and pitfalls: [reference.md](reference.md#description-snippets-and-failures).

## Principles

- **Single responsibility** — Compose multiple skills instead of one mega skill.
- **One-liners** — Each section earns its tokens; subsection titles + tight bullets; defer essays to `reference.md`.
- **Progressive disclosure** — Keep **`SKILL.md` ≤ ~300 lines**; split oversized content into `reference.md` / `examples.md` (prefer **single-level** links from `SKILL.md`).
- **Self-improvement** — After errors or strong user feedback, update this meta-skill or the child skill accordingly.

### Degrees of freedom

| Level | When | Example |
|-------|------|---------|
| High | Several valid approaches | Code review judgement |
| Medium | Preferred pattern, some slack | Report template |
| Low | Fragile or compliance-sensitive steps | Scripted migration |

## SKILL.md body shape (minimal template)

Use this scaffold when starting a new skill:

```markdown
---
name: example-skill
description: Does X in third person. Use when Y or Z.
---

# Title

## When to use
- …

## Instructions
1. …

## Output format (if needed)
…

## Additional resources
- [reference.md](reference.md)
```

## Architecture-aligned skills

For skills that encode architecture workflows, align with arc42 themes (sections 1–12): goals, constraints, context, solution strategy, building blocks, runtime, deployment, crosscutting concepts, decisions, quality, risks, glossary.

## Next steps for the agent

1. Resolve discovery items above (or infer safely), including step 7 when the change is new or a substantial rewrite.
2. Draft `SKILL.md` respecting size and linking rules.
3. Add `reference.md` / `examples.md` / `scripts/` only when justified.
4. Run the checklist in [reference.md](reference.md#pre-merge-checklist).
5. In `pkuppens/skills`: `skills-ref validate skills/<name>` (policy: [ADR 001](../../../docs/decisions/001-skill-validation-and-tooling.md)), add a row to [SKILL_TREE.md](../../SKILL_TREE.md), and add a plugin entry to `.claude-plugin/marketplace.json` (one plugin per skill).
