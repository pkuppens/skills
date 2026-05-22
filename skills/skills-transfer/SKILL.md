---
name: skills-transfer
description: >-
  Guides intake of Agent Skills from Git repos, skills.sh, and pkuppens/pkuppens into
  IDE paths or this library. Covers project vs global install, derivative skills, and
  catalog maintenance. Use when installing, adapting, or contributing skills.
---

# Skills transfer

Move skills between sources (public registry, Git repos, this library) and agent environments without duplicating the [Agent Skills specification](https://agentskills.io/specification).

## When to use

- Install skills from [skills.sh](https://www.skills.sh/), `npx skills add`, or symlink
- Bring skills from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) or other repos into a project
- Create a **derivative skill** that references a canonical or public base skill
- Maintain the library **catalog** (`SKILL_TREE.md`, bundles, optional skills.sh listing)
- Migrate a **whole tree** into `pkuppens/skills` → activate nested skill [repo-transfer](repo-transfer/SKILL.md)

## Quick path

1. **Discover** — `npx skills find <keywords>` or browse skills.sh; check [sources](references/sources.md).
2. **Choose install scope** — project vs global: [install-modes](references/install-modes.md).
3. **Reuse or build** — prefer install when a public skill fits; author only the delta (see [derivative-skills](references/derivative-skills.md)).
4. **Validate** — `skills-ref validate <skill-dir>` (same check as CI).
5. **Contribute here** — follow [repo-transfer](repo-transfer/SKILL.md) for PRs into this library.

## Derivative skills (summary)

Do not edit canonical skills in place when you only need a personal or team variant. Add a new folder with its own `name` and `description`, and link to the base skill in the body. See [examples.md](examples.md) and [derivative-skills](references/derivative-skills.md).

## Catalog (summary)

Keep `skills/SKILL_TREE.md` aligned with folders under `skills/`. Optional curated sets live under `docs/bundles/` (planned). Optional promotion on skills.sh is marketing, not required for merge. Details: [catalog](references/catalog.md).

## Additional resources

- [install-modes.md](references/install-modes.md) — symlink, Skills CLI, project vs global
- [sources.md](references/sources.md) — pkuppens/pkuppens, skills.sh, arbitrary Git
- [derivative-skills.md](references/derivative-skills.md) — wrap/reference pattern, upstreaming
- [catalog.md](references/catalog.md) — SKILL_TREE, bundles, skills.sh
- [examples.md](examples.md) — derivative skill sketch
- [repo-transfer/SKILL.md](repo-transfer/SKILL.md) — land a repo skills tree here
