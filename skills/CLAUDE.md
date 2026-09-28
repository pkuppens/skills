# skills/ — Agent instructions

Rules for working inside `skills/`. Cross-cutting process (issue scoping, verification, avoiding duplication) lives in the [root CLAUDE.md](../CLAUDE.md); don't restate it here.

## Scope

This directory holds the portable Agent Skills for Cursor, Claude, and Codex. Consumers link or install them via symlink, the Skills CLI, or the Claude Code plugin marketplace (see the [repository README](../README.md)).

## Structure

- One skill per directory, each with a `SKILL.md`. Nested trees are allowed (e.g. [terminal/](terminal/SKILL.md) routes to shell leaves).
- Index: [SKILL_TREE.md](SKILL_TREE.md)
- How skills compose: [COOPERATION.md](COOPERATION.md)
- Meta-skills and notes: [_meta/](_meta/) — [skill-creation](_meta/skill-creation/SKILL.md), [human-ai-execution](_meta/human-ai-execution.md)

## Creating or editing skills

1. Use [skill-creation](_meta/skill-creation/SKILL.md) for new skills. Check first whether a published skill already fits (install before authoring).
2. Follow the [Agent Skills specification](https://agentskills.io/specification) and [Claude skill best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices#skill-structure): YAML frontmatter with `name` (matching the folder) and `description`, concise body, progressive disclosure. Quote `description` when it contains colons.
3. Keep `SKILL.md` under ~300 lines; move detail to `reference.md` / `references/`, or split into smaller skills.
4. Register every new skill in [SKILL_TREE.md](SKILL_TREE.md) and as its own plugin in `.claude-plugin/marketplace.json`.

## Validation

Validation policy: [ADR 001 — Skill validation and tooling](../docs/decisions/001-skill-validation-and-tooling.md). CI (`.github/workflows/validate-skills.yml`) runs `skills-ref validate` on every skill directory and `claude plugin validate . --strict` on the marketplace manifest. Run the same locally before opening a PR:

```bash
npx --yes skills-ref validate skills/<name>
```

## Scratch

Scratch files (research, drafts, skill reflection) go in `tmp/skills/` at the repo root, not in `skills/`.
