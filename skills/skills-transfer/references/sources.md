# Skill sources

## This library (`pkuppens/skills`)

Canonical skills under `skills/<name>/`. CI validates every `SKILL.md` under `skills/`. Contribute via PR (see [repo-transfer](../repo-transfer/SKILL.md)).

## Monorepo migration source (`pkuppens/pkuppens`)

Skills still live in the profile repo during [epic #90](https://github.com/pkuppens/pkuppens/issues/90). When copying into this library:

- One skill per directory; `name` matches directory
- Split large bodies into `references/` per [agentskills.io](https://agentskills.io/specification)
- Open a PR here; do not commit duplicate trees in both repos long term

## skills.sh and ecosystem packages

Browse [skills.sh](https://www.skills.sh/) or run:

```bash
npx skills find "<keywords>"
```

Install published skills into the **consumer** environment:

```bash
npx skills add https://github.com/<owner>/<repo> --skill <slug> -y
```

Prefer **reuse** when a public skill fits; document the install command in project docs. License and attribution apply when copying text into this library.

## Arbitrary Git URLs

Any repo with `skills/<dir>/SKILL.md` layout can be listed and installed:

```bash
npx skills add https://github.com/<owner>/<repo> --list -y
```

Pin installs with `@<ref>` on `owner/repo` in **consumer** docs when reproducibility matters; this library’s CI does not pin npm tooling (see ADR 001).
