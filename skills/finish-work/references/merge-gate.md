# Merge gate: the commands

The gate is **green CI on the head commit, plus the sign-off the repo calls
for**: an `APPROVE` where a review is enforced (section 1), the user's
instruction to land where it is not (section 2). Every check below is keyed to
one SHA, read once at the start:

```bash
SHA=$(gh pr view <pr> --json headRefOid --jq .headRefOid)
```

## 0. Is an approval enforced?

Branch protection and rulesets are separate APIs; a repo can use either. Ask
both, for the base branch:

```bash
BASE=<base>
bp=$(gh api repos/{owner}/{repo}/branches/$BASE/protection \
  --jq '.required_pull_request_reviews.required_approving_review_count // 0' 2>&1) \
  || { case $bp in *"Branch not protected"*) bp=0;; *) bp=unknown;; esac; }
rs=$(gh api repos/{owner}/{repo}/rules/branches/$BASE \
  --jq '[.[] | select(.type == "pull_request") | .parameters.required_approving_review_count] | max // 0' 2>&1) \
  || rs=unknown
for v in bp rs; do case ${!v} in ''|*[!0-9]*) printf -v "$v" unknown;; esac; done
echo "protection=$bp rulesets=$rs"
```

Not enforced only when **both** are `0`. Any number of 1 or more is enforced.
`unknown` (a failed read, or anything that is not a number) is enforced: the
protection endpoint answers `Not Found`, not `Branch not protected`, to a login
without admin rights, so a failed read proves nothing. Example outputs seen on
2026-11-27, which repo settings can change: `pkuppens/skills` gives `0 0` (not
enforced); `pkuppens/babblr` answers `Branch not protected` (not enforced);
`microsoft/vscode` rulesets give `2` (enforced) and its protection endpoint
answers `Not Found` to a non-admin (so `unknown`, also enforced).

## 1. Approval on the head SHA (when enforced)

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
the new commits, unless it carries over (next section).

### Carrying an approval over a trivial rebase

Before calling an approval stale, check whether the PR's own change is
unchanged. A rebase onto a newer base, or a merge of the base into the branch,
moves the head SHA but not what was reviewed. Compare the stable patch-id of
the PR's own diff at the approved SHA and at the current head:

```bash
OLD=<commit_id of the approval>
git fetch origin "$OLD" <base>   # fails if GitHub no longer serves it: stale
pid() { git diff "$(git merge-base origin/<base> "$1")" "$1" | git patch-id --stable | cut -d' ' -f1; }
[ "$(pid "$OLD")" = "$(pid "$SHA")" ] && echo "carry over" || echo "stale"
```

Equal ids mean the same hunks, ignoring line numbers and blob hashes, so the
approval carries over to `$SHA`. Different ids, or an `$OLD` that cannot be
fetched, mean stale: re-approve. Conflict resolutions that changed content and
any new commit change the id, so they are never carried. A `CHANGES_REQUESTED`
review is never carried over. The carry-over covers only the approval: CI
(section 3) and threads and freshness (section 4) are still checked on `$SHA`,
which is what catches a base change that interacts with the PR. Report both
SHAs and the patch-id. `git range-diff "$OLD"...$SHA` is the human-readable
view when the ids differ and you want to see why.

## 2. Self-authored PRs, and the merge instruction when approval is not enforced

```bash
ME=$(gh api user --jq .login)
AUTHOR=$(gh pr view <pr> --json author --jq .author.login)
[ "$ME" = "$AUTHOR" ] && echo "self-authored: $ME opened this PR, APPROVE is impossible"
```

When they match, `gh pr review --approve` fails with *"Can not approve your
own pull request"*. If approval is **enforced**, only the bot flow (#45) or
another approver can satisfy it (a comment review does not), so stop and tell
the user. If it is **not enforced**, the sign-off is the user's instruction to
merge (the accepted wording is in SKILL.md step 5). Record it as a PR comment on
the head SHA, quoting their words. **The comment is an audit record only**:
verify the sign-off against the user's chat message in this session or a
user-authored review, never against this comment, which carries the agent's
marker. Keep the SHA: freshness is the patch-id check above, run between that
SHA and the head.

```bash
gh pr comment <pr> --body "Merge instruction from the user: \"<their words>\". Head <sha>. Approval is not enforced here (protection=0 rulesets=0). <!-- finish-work:agent -->"
```

A user **comment review** that is clearly positive ("LGTM", "OK", "approved",
"looks good") is an equal sign-off (only reviews and chat count, not plain PR
comments).
List the candidates, leaving out everything the agent posted (marker
`<!-- finish-work:agent -->`):

```bash
gh api repos/{owner}/{repo}/pulls/<pr>/reviews --paginate \
  --jq '[.[] | select(.user.login == "'"$ME"'" and .commit_id == "'"$SHA"'"
        and (.body | contains("<!-- finish-work:agent -->") | not))]
        | max_by(.submitted_at) // empty | {id, state, submitted_at, body}'
```

Read the body of the latest one. It counts as the instruction when its state
is `COMMENTED` or `APPROVED` and its body is clearly positive ("LGTM", "OK",
"approved", "looks good"; merge wording is not needed in a review). It does not count when it is
empty, asks a question, requests a change, or mixes praise with a "but". In
that case, ask the user; never infer approval. A review on an older
`commit_id` is stale, the same as a stale `APPROVE`. Quote the review body
and its id in the report.

**A pending review hides its comments.** While the user's review is pending,
the REST `reviews` and `pulls/<pr>/comments` calls do not return its comments,
and replying to a review comment fails with HTTP 422. Read the threads through
GraphQL (`pullRequest.reviewThreads { nodes { isResolved comments(first:20)
{ nodes { body author { login } } } } }`, as in step 4 below) and answer with a
plain PR comment (`gh pr comment`) that quotes what it replies to.

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

**Replying and resolving.** Reply on each human thread you act on, with what
changed and the commit SHA. Do not resolve the thread: the reviewer who opened
it does that. Threads still open after your replies are not a failure of the
reply; report them and ask the user. Never resolve them to pass the gate.

```bash
gh api -X POST repos/<owner>/<repo>/pulls/<pr>/comments/<comment-id>/replies -f body="<what changed> (<sha>)"
```

`<comment-id>` is the id of the thread's first comment (`pulls/<pr>/comments`).
For a pending review, use the plain PR comment from section 2 instead.

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
