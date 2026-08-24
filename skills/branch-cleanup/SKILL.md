---
name: branch-cleanup
description: Clean Git branches after a merged PR or before new work. Prune stale remotes and remove safely merged branches. Use for repo cleanup, branch cleanup, tidy, or prune.
---

# Branch Cleanup

Repeatable branch hygiene for a git repo: prune stale remote-tracking refs,
bring local branches up to date, then delete anything fully merged into the
main branch. Reports what it can't safely resolve instead of forcing past it.

For GitHub Actions workflow-run cleanup, use the separate `clean-ci-runs`
skill — this skill only touches branches.

## Steps

1. `git fetch --all --prune` — drop remote-tracking refs for branches deleted
   upstream.
2. Fast-forward every local branch from its upstream (`git fetch <remote>
   <branch>:<branch>` for non-checked-out branches; `git merge --ff-only` for
   the checked-out one). Branches that have diverged from their upstream are
   left untouched — this only ever fast-forwards.
3. Delete local and remote branches that are fully merged into the repo's
   main branch (`main` or `master`, whichever exists). A local branch is a
   candidate either because it's a true git-ancestor merge, or because its
   upstream was deleted (`[gone]`) — the latter catches squash-merge
   workflows where no ancestor relationship exists. Deletion still uses
   `git branch -d` (never `-D`), so a `[gone]` branch that git can't verify
   as merged is reported as unresolved rather than force-deleted. If the
   currently checked-out branch is itself a deletion candidate, the script
   switches to main first (git refuses to delete a checked-out branch), so
   the user ends up on main instead of a dangling deleted branch.
4. Report anything unresolved — permission errors on remote deletion,
   branches that failed to fast-forward, branches `git branch -d` refused —
   instead of retrying with force flags.

Protected branches, never touched: `main`, `master`, `develop`,
`development`, `staging`, `production`, `release/*`, `hotfix/*`.

## Usage

Run [cleanup-branches.sh](cleanup-branches.sh) from within the target repo
(Git Bash on Windows, or bash/zsh elsewhere):

```bash
./cleanup-branches.sh              # dry-run (default) - report only
./cleanup-branches.sh --execute    # perform the cleanup
./cleanup-branches.sh --local-only # skip remote branch deletion
./cleanup-branches.sh --help
```

**Always dry-run first** and read the output before passing `--execute`.

Requirements: `git`; `gh` CLI recommended as a fallback path when `git push
origin --delete` is rejected for auth reasons but the `gh` session has
sufficient permission.

## When invoked as an agent skill

1. Confirm the working directory is the intended repo (`git remote -v`).
2. Run the script without `--execute` and show the user the plan.
3. Only run with `--execute` after the user confirms, or if the invoking
   context already authorized destructive branch cleanup.
4. Summarize what was deleted and list anything in the "Unresolved" section
   verbatim — don't silently drop it or try to work around it (e.g. don't
   fall back to `git push --force` or repo admin API calls beyond the `gh
   api` delete-ref fallback already in the script).

## Notes

- Fast-forwarding local branches (step 2) never touches the working tree
  except for the currently checked-out branch, where `git merge --ff-only`
  is used — it fails loudly rather than creating a merge commit if history
  has diverged.
- "Merged into main" is computed against `origin/main` (or `origin/master`)
  when that remote-tracking ref exists, else the local main branch.
- This skill supersedes ad hoc per-repo copies of a branch-cleanup script
  (e.g. `scripts/cleanup-merged-branches.sh` in `pkuppens/babblr`) — prefer
  installing this skill over maintaining a project-local fork.
