# Pull request workflow (this library)

## Branch protection (target state)

- Pull request required to merge to `main`
- Status check **Validate skills** must pass
- No required approving reviewer (solo maintainer)

## Before opening a PR

```bash
# From repo root, after Node is available
npm install -g skills-ref
skills-ref validate skills/<each-changed-skill-dir>
npx skills add https://github.com/pkuppens/skills --list -y
```

## Commits

- Reference issue: `#1: chore: unpinned validate-skills CI`
- Small logical commits; avoid unrelated changes

## PR description

- Link issue (`Closes #1` or `Refs #1`)
- List new/changed skill directories
- Note catalog updates (`SKILL_TREE.md`, README)

## Issue comments (significant steps)

1. Post implementation **plan** once (grill decisions + breakdown)
2. Post **PR link** when the branch is pushed
3. Post **final validation** when merged: PR URL, merge SHA, green CI run link, local validate commands used

## After merge

- Sync `main` locally; delete feature branch
- Confirm **Validate skills** green on `main`
