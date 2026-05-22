---
name: repo-transfer
description: >-
  Migrates a repository skills tree into pkuppens/skills with agentskills.io layout,
  validation, and pull-request workflow. Use when landing skills from pkuppens/pkuppens
  or another Git repo into this skill library.
---

# Repo transfer

Sub-skill of [skills-transfer](../SKILL.md). Use when the deliverable is a PR to **this** repository, not only a local IDE install.

## When to use

- Copy or move skill folders from `pkuppens/pkuppens` (or elsewhere) into `pkuppens/skills/skills/`
- Add nested skills (e.g. `skills/skills-transfer/repo-transfer/`) — each folder with `SKILL.md` is validated separately in CI
- Ensure layout matches [agentskills.io](https://agentskills.io/specification) before merge

## Workflow

1. Branch from `main`: `chore/<issue>-short-title` or `feature/<issue>-short-title`
2. Place skills under `skills/<directory>/` with `name` equal to `<directory>`
3. Keep each `SKILL.md` lean; use `references/`, `examples.md`, `scripts/`, `assets/` per [layout](references/layout.md)
4. Run locally: `skills-ref validate skills/<directory>` for each new/changed skill
5. Commit with `#<issue>: type: message`; push; open PR (required once branch protection is on)
6. Wait for **Validate skills** on the PR; fix forward if floating tooling breaks CI
7. Update `skills/SKILL_TREE.md` and catalog docs in the same PR when applicable

## Additional resources

- [layout.md](references/layout.md) — directory shape, progressive disclosure
- [pr-workflow.md](references/pr-workflow.md) — commits, checks, issue comments
