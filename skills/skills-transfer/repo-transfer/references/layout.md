# Skill directory layout

Per [Agent Skills specification](https://agentskills.io/specification):

```text
skill-name/
├── SKILL.md          # required: frontmatter + instructions
├── references/       # optional: loaded on demand
├── examples.md       # optional: at skill root (one level from SKILL.md)
├── scripts/          # optional: executables
└── assets/           # optional: templates, static data
```

## Rules

- YAML `name` must match the **immediate parent directory** name.
- Keep `SKILL.md` under ~500 lines; move detail to `references/*.md`.
- Link from `SKILL.md` with relative paths **one level deep** (e.g. `[guide](references/guide.md)`), not chains of references.
- Use forward slashes in paths for cross-platform installs.

## Nested skills in this library

CI runs `find skills -name SKILL.md` and validates **each** directory. Nested paths such as `skills/skills-transfer/repo-transfer/` are valid if frontmatter and layout pass `skills-ref validate`.

The Skills CLI `--list` smoke test may only show top-level discoverable skills; nested skills are still required to pass validation when present.

## Progressive disclosure

1. **Metadata** — `name`, `description` (loaded at startup for discovery)
2. **SKILL.md body** — loaded on activation
3. **references/, scripts/, assets/** — loaded only when instructions say so
