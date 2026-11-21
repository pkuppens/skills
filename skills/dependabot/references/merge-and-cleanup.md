# Merge strategy and branch cleanup

Disclosed reference for [`SKILL.md`](../SKILL.md) Step 8.

## Merge strategy

Prefer rebase: these PRs are one logical commit from a bot, and a rebase
keeps Dependabot's own commit (release-notes trailer, signature) on the base
branch. Squash is acceptable when the repo disallows rebase, or when its
history is squash-only. Say which strategy you used in the report. Use
`--squash` in place of `--rebase`. Never use a merge commit unless it is the
only allowed strategy. Check what the repo allows:

```bash
gh repo view <repo> --json rebaseMergeAllowed,squashMergeAllowed,mergeCommitAllowed,deleteBranchOnMerge
```

`gh` reports a disallowed strategy. Try the next one in that order, never a
strategy the repo has not enabled.

## Branch cleanup

`--delete-branch` removes the PR's own branch. It does not remove leftovers:
a closed or superseded group PR, or a repo with auto-delete off. After the
merges, list what is left and delete only branches whose PR is merged or
closed:

```bash
git ls-remote --heads origin 'dependabot/*'
gh pr list --repo <repo> --state open --search "head:dependabot/" --json headRefName
```

Anything on the first list but not the second has no open PR. Delete it with
`git push origin --delete <branch>` after checking `gh pr list --state all
--head <branch>` shows it merged or closed. The `branch-cleanup` skill does
the same for local branches.
