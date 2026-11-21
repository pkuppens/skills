# Merge strategy and branch cleanup

Disclosed reference for [`SKILL.md`](../SKILL.md) Step 8.

## Merge strategy

Prefer squash, authored by you. A squash commit takes the author you pass
with `--author-email`; a rebase replays Dependabot's own commit and can never
count as yours. Use your GitHub noreply address, so your personal email stays
out of public history:

```bash
gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"'
```

A squash commit that carries an email linked to your account counts as a
contribution once it is on the default branch. What it loses is Dependabot's
own signature and trailer. The PR keeps the release notes, so put the bumped
packages and the PR URL in the commit body. Cleanup is the same as for a
rebase: `--delete-branch` and the repo's delete-on-merge setting remove the
branch. Fall back to rebase when the repo disallows squash, and say in the
report that the commit stays Dependabot's. Never use a merge commit unless it
is the only allowed strategy. Check what the repo allows:

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
