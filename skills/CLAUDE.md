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
5. **Define terms once, in [CONTEXT.md](../CONTEXT.md), and link them.** If a skill uses a term that has a CONTEXT.md entry, link that entry at the term's **first** use in the skill — `[test oracle](../../CONTEXT.md#language-legacy-refactoring)`. Do not restate the definition: two copies drift, and an agent that reads only one of them gets the stale one. If a skill needs a term that CONTEXT.md does not define yet, add the entry there first. Terms that read as ordinary English but carry a precise meaning (`oracle`, `sound`, `recall`, `call site`) need this most, because an agent will otherwise supply the everyday meaning.
6. State what proves the skill works. Give each skill a `**Status:**` line saying whether a real run has exercised it, and link that evidence. A skill with no evidence yet says so — never imply a run that did not happen.

## Validation

Validation policy: [ADR 001 — Skill validation and tooling](../docs/decisions/001-skill-validation-and-tooling.md). CI (`.github/workflows/validate-skills.yml`) runs `skills-ref validate` on every skill directory and `claude plugin validate . --strict` on the marketplace manifest. Run the same locally before opening a PR:

```bash
npx --yes skills-ref validate skills/<name>
```

## Scratch

Scratch files (research, drafts, skill reflection) go in `tmp/skills/` at the repo root, not in `skills/`.
