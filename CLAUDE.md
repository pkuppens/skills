# Working in `pkuppens/skills`

Repo-wide guidance for agents and contributors. This file owns **cross-cutting process** (how to scope work, verify it, and avoid duplication across issues/docs). Skill-authoring and validation policy lives in [skills/CLAUDE.md](skills/CLAUDE.md), which links back here for anything cross-cutting rather than restating it.

For domain vocabulary (what terms like "Catalog", "Skills transfer", "Canonical skill" mean), see [CONTEXT.md](CONTEXT.md) — this file is process, not glossary.

## Process lessons

**Keep issues small and closeable.** An issue with acceptance criteria that depend on unrelated future work (another issue, another epic) will never fully close. If a criterion is blocked or already owned elsewhere, cut it and reference the other issue instead of leaving a dangling checkbox.
_Why:_ issue #2 originally bundled a README/symlink/CLI audit with a criterion that depended on files owned by #7 — splitting it let #2 close on its own merits.

**Write acceptance criteria that can be verified by inspection, not assumption.** Prefer criteria that name a concrete check (grep for a string, diff against a real file) over vague language ("stays aligned", "matches reality"). When a criterion turns out to be unverifiable as written (e.g. it names a version or file that doesn't exist in the repo), rewrite it against what actually exists before implementing.
_Why:_ issue #2 referenced `npx skills@1.5.6`, which never appeared anywhere in the repo — rewriting the criterion against the real CI invocation in `.github/workflows/validate-skills.yml` made it checkable.

**Reference other issues/docs instead of duplicating scope.** Before adding a checkbox or a doc section, check whether an existing issue or file already owns that work (`gh issue list --search ...`, grep the docs). Link to it rather than re-describing it in two places.
_Why:_ `docs/curated-skill-selection.md` / `docs/bundles/` cross-linking was already the entire scope of issue #7 — issue #2 only needed to reference #7, not restate the task.

## Repo structure (high level)

- `README.md` — GitHub landing page: usage, IDE setup, Skills CLI install.
- `CONTEXT.md` — domain glossary only.
- `docs/decisions/` — ADRs (hard-to-reverse, non-obvious, real-tradeoff decisions only).
- `docs/agents/` — issue tracker, triage labels, and domain-doc rules the engineering skills read.
- `skills/` — the actual Agent Skills tree (`SKILL_TREE.md` index, per-skill folders). [skills/CLAUDE.md](skills/CLAUDE.md) (agent rules), [skills/COOPERATION.md](skills/COOPERATION.md) (how skills compose), `skills/_meta/` (skill-creation, human-ai-execution).
- `workshops/` — worked examples that prove a skill set works, as notebooks with their cell output committed. Rules: [workshops/legacy-refactor/notebooks/README.md](workshops/legacy-refactor/notebooks/README.md). **Never add `nbstripout` to this repo** — it deletes the stored output these examples depend on.

Defer subdirectory-specific instructions to files within that subdirectory once they exist; this file stays high-level.

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `pkuppens/skills`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage roles, each label named after its role (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` plus ADRs in `docs/decisions/`. See `docs/agents/domain.md`.
