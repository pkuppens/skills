# Merge gate: the commands

The gate is **approval and green CI on the same head commit**. Every check
below is keyed to one SHA, read once at the start:

```bash
SHA=$(gh pr view <pr> --json headRefOid --jq .headRefOid)
```

## 1. Approval on the head SHA

`reviewDecision` is the quick check:

```bash
gh pr view <pr> --json reviewDecision --jq .reviewDecision   # want: APPROVED
```

It is not enough on its own. GitHub fills `reviewDecision` only when branch
protection requires reviews; with `required_approving_review_count: 0` it is
an empty string even after an approval. It also stays `APPROVED` after a push
unless protection dismisses stale approvals. So check the latest review state
per reviewer, and the commit each review was given on:

```bash
gh api repos/{owner}/{repo}/pulls/<pr>/reviews --paginate \
  --jq '[.[] | select(.state != "COMMENTED")] | group_by(.user.login)
        | map(max_by(.submitted_at)) | .[] | {user: .user.login, state, commit_id}'
```

Pass when at least one reviewer's latest state is `APPROVED` with
`commit_id == $SHA`, and no reviewer's latest state is `CHANGES_REQUESTED`.
An approval with another `commit_id` is stale: approve again after checking
the new commits.

## 2. Self-approval

```bash
ME=$(gh api user --jq .login)
AUTHOR=$(gh pr view <pr> --json author --jq .author.login)
[ "$ME" = "$AUTHOR" ] && echo "self-approval impossible: $ME authored this PR"
```

When they match, `gh pr review --approve` fails with *"Can not approve your
own pull request"*. That is the end of the agent's part: use the bot flow
(#45) or ask the user. It never turns into a merge without an approval.

## 3. Green CI on the head SHA

```bash
gh pr checks <pr> --watch --fail-fast         # blocks until done; no polling loop
gh pr view <pr> --json headRefOid,statusCheckRollup \
  --jq '{sha: .headRefOid, checks: [.statusCheckRollup[] | {name: (.name // .context), conclusion: (.conclusion // .state)}]}'
```

Pass when `sha == $SHA` and every conclusion is `SUCCESS`, `SKIPPED` or
`NEUTRAL`. The exit code of `gh pr checks --watch` is not the verdict; read
the conclusions. Required check names come from branch protection
(`required_status_checks.contexts`, see [repo-facts.md](repo-facts.md)); a
required check that never reported is a failure, not a pass.

## 4. Threads and freshness

```bash
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
  reviewThreads(first:100){nodes{isResolved}}}}}' -F o=<owner> -F r=<repo> -F n=<pr> \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)] | length'   # want: 0

gh pr view <pr> --json mergeable,mergeStateStatus   # want: MERGEABLE, not BEHIND/DIRTY
```

`BLOCKED` means a protection rule is not yet satisfied; after the checks above
pass it usually names the missing approval. `UNKNOWN` means GitHub has not
computed it yet: query again once or twice before treating it as a failure.

## 5. Merge, pinned to the SHA

```bash
gh pr merge <pr> --rebase --delete-branch --match-head-commit "$SHA"
```

`--match-head-commit` makes the merge fail if anyone pushed after the gate was
checked, which closes the gap between checking and merging. Use `--squash`
when rebase-merge is not allowed. Under a merge queue use `--auto` and then
confirm `state == MERGED`.

**Stacked PRs:** deleting a PR's base branch closes the PRs on top of it. Merge
the lower PR without `--delete-branch`, retarget the upper PR to `main`, then
delete the branch.
