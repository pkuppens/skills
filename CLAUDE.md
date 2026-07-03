# Working in `pkuppens/skills`

Repo-wide guidance for agents and contributors. This file owns **cross-cutting process** (how to scope work, verify it, and avoid duplication across issues/docs). Skill-validation-specific policy belongs in `skills/CLAUDE.md` once it migrates ([#5](https://github.com/pkuppens/skills/issues/5)) — that file should link back here for anything not specific to skill validation, rather than restating it.

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
- `docs/curated-skill-selection.md`, `docs/bundles/` — planned, owned by [#7](https://github.com/pkuppens/skills/issues/7).
- `skills/` — the actual Agent Skills tree (`SKILL_TREE.md` index, per-skill folders). `skills/CLAUDE.md` and `skills/COOPERATION.md` are planned migration targets ([#5](https://github.com/pkuppens/skills/issues/5)).

Defer subdirectory-specific instructions to files within that subdirectory once they exist; this file stays high-level.
