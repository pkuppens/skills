---
name: branch-cleanup
description: Clean Git branches after a merged PR or before new work. Prune stale remotes and remove safely merged branches. Use for repo cleanup, branch cleanup, tidy, or prune.
---

# Branch Cleanup

Repeatable branch hygiene for a git repo: refresh every local branch (main
first in importance), verify each branch's *content* against main, then
delete local and remote branches that carry nothing main doesn't already
have. Ends on a fresh main and reports what it did, what it kept, and the
final state. Never forces past anything it can't verify.

For GitHub Actions workflow-run cleanup, use the separate `clean-ci-runs`
skill — this skill only touches branches.

## Steps (and why in this order)

0. **Preflight** — record the checked-out branch, whether its working tree
   has uncommitted/unstaged/untracked changes, and branches checked out in
   other worktrees. Nothing is switched yet: switching first would carry a
   dirty tree onto main or fail.
1. **Fetch** — `git fetch --all --prune`. The only network step; drops
   remote-tracking refs for branches deleted upstream, which is what marks
   local branches `[gone]`. (This is the "pull" half of "switch to main and
   pull" — done before switching so main is already fresh when checked out.)
2. **Refresh** — fast-forward every local branch, main included, from its
   upstream without checking it out (`git fetch . <upstream>:<branch>`; for
   the checked-out branch, `git merge --ff-only`). Diverged branches are
   reported, never merged.
3. **Verify** — classify every non-protected branch against `origin/main`:
   - `merged` — the branch is an ancestor of main.
   - `squash-merged` — merging it into main would change nothing
     (`git merge-tree --write-tree` result equals main's tree), i.e. all of
     its changes are already in main. Catches squash/rebase merges.
   - `pr-merged #N` — a merged GitHub PR had this branch as its head, and
     either its head commit contains the branch tip, or (if the PR was
     rebased before merging) it makes exactly the same line changes
     (zero-context patch-id against `refs/pull/N/head`). Catches squash
     merges whose files main has edited since, which `merge-tree` can't
     prove. Needs `gh`; a commit added after the merge fails both checks.
   - `unmerged` — it has changes main doesn't: **kept**. If its upstream is
     also gone, it is reported as unresolved so it gets a human look.

   A merged local branch is still kept if it is the current branch with
   uncommitted/unstaged/untracked changes, or checked out in another
   worktree.
4. **Switch** to the fresh main — skipped when the working tree has changes,
   or with `--stay` (unless the current branch is being deleted).
5. **Delete** verified local branches (`git branch -D`: plain `-d` can't see
   squash merges, so step 3 does the verification and the old tip is logged
   for restore), then verified `origin` branches (`git push --delete`, with
   a `gh api` delete-ref fallback).
6. **Report** — actions taken with restore commands, kept branches,
   unresolved items, and final state (current branch, `git branch -vv`,
   origin branches, stash count). Stash entries made on a deleted branch are
   noted — they survive deletion.

Protected branches, never touched: `main`, `master`, `develop`,
`development`, `staging`, `production`, `release/*`, `hotfix/*`.

## Usage

Run [cleanup-branches.sh](cleanup-branches.sh) from within the target repo
(Git Bash on Windows, or bash/zsh elsewhere):

```bash
./cleanup-branches.sh              # dry-run (default) - plan only
./cleanup-branches.sh --execute    # perform the cleanup
./cleanup-branches.sh --local-only # skip remote branch deletion
./cleanup-branches.sh --stay       # don't switch to main at the end
./cleanup-branches.sh --help
```

**Always dry-run first** and read the plan before passing `--execute`. The
dry-run still performs the step-1 fetch/prune (it only updates
remote-tracking refs) so the plan reflects the remote's current state.

Requirements: `git` (2.38+ for the `merge-tree` squash check; older versions
fall back to a `git cherry` patch-id check, which misses squashes that main
later modified). `gh` CLI recommended: it supplies the merged-PR list for the
`pr-merged` check (without it, such branches are kept as unresolved), and is
the fallback when `git push origin --delete` is rejected for auth reasons.

To verify the script end-to-end without touching a real repo, run
[tests/test-cleanup.sh](tests/test-cleanup.sh): it builds a throwaway repo
with a local bare `origin` and a fake `gh` (merged, squash-merged,
PR-merged after main edited the same files, rewritten-then-merged, unmerged,
behind and
dirty branches), runs dry-run and `--execute`, and prints PASS/FAIL per
check.

## When invoked as an agent skill

1. Confirm the working directory is the intended repo (`git remote -v`).
2. Run the script without `--execute` and show the user the plan.
3. Only run with `--execute` after the user confirms, or if the invoking
   context already authorized destructive branch cleanup.
4. Relay the report: actions (with restore commands), kept branches, and the
   "Unresolved" section verbatim — don't silently drop items or work around
   them (no `git push --force`, no admin API calls beyond the script's `gh
   api` delete-ref fallback).

## Notes

- Content is verified against `origin/main` (or `origin/master`) when that
  remote-tracking ref exists, else the local main branch.
- A branch with no commits beyond main (e.g. just created for new work) is
  `merged` by definition and will be deleted — nothing is lost, but commit
  or push first if you want to keep the name.
- A remote branch is deleted on the same content rule, so a squash-merged
  PR branch GitHub didn't auto-delete is cleaned up too.
- This skill supersedes ad hoc per-repo copies of a branch-cleanup script
  (e.g. `scripts/cleanup-merged-branches.sh` in `pkuppens/babblr`) — prefer
  installing this skill over maintaining a project-local fork.
