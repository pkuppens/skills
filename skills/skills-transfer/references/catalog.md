# Catalog maintenance

The **catalog** is how humans and agents find skills in this library.

## Required (in-repo)

| Artifact | Purpose |
|----------|---------|
| `skills/<name>/` | Source of truth per skill |
| `skills/SKILL_TREE.md` | Hierarchical index (populate as migration PRs land) |
| `skills/README.md` | Pointer to conventions and README install section |
| Root `README.md` | GitHub landing, install, validation summary |

When adding or renaming a skill folder, update `SKILL_TREE.md` in the same PR.

## Planned (epic #90)

| Artifact | Purpose |
|----------|---------|
| `docs/bundles/` | Curated sets (e.g. “portfolio sprint”, “healthcare”) |
| `docs/curated-skill-selection.md` | How to pick bundles |

## Optional (not a merge gate)

| Channel | Purpose |
|---------|---------|
| [skills.sh](https://www.skills.sh/) | Discovery/marketing for published packages |
| `metadata.version` in frontmatter | Skill-level semver hint only; does not control Git clone ref |

CI validates spec compliance, not skills.sh listing.
