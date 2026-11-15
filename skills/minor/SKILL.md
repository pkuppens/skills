---
name: minor
description: 'Autonomously complete a minor GitHub issue end to end - validate it, decide the open questions yourself, record the decisions as issue comments, implement, open a PR with a session transcript, and merge. Use whenever the user wants an issue finished without being asked questions: "/minor 42", "take issue 17 to a PR", "close out the open issues yourself", "complete these without me", "just make the call and ship it", or any batch cleanup of a backlog they have deprioritised. Also use when the user says a task is minor, low-stakes, or revisitable, which is their signal that your judgment is enough and they do not want to be consulted.'
---

# Minor

Take a minor GitHub issue from open to merged without asking the user anything.

"Minor" is the user's judgment, not yours. When they call an issue minor they are
delegating the decisions inside it, not the decision about whether it matters.
That delegation is the whole point of this skill: the cost of a wrong call is low
and revisitable, and the cost of stopping to ask is a stalled backlog.

So the default is to decide and proceed. The thing you owe them in exchange is a
**legible record**: anyone reading the issue afterwards should understand what you
chose, why, and what you rejected — without reading your diff or this transcript.

## The one hard stop

Decide and proceed, except where proceeding would be **unsafe, destructive beyond
the issue's scope, or outward-facing in a way the user cannot walk back**. Examples
that are not yours to decide, however minor the issue:

- publishing, deploying, or sending anything to a third party or to real users
- rotating, revoking, or exposing a credential
- deleting data, branches, or history outside the branch you created
- anything touching real personal data, where the safe default is to use synthetic
  data and say so

Hitting one of these does not mean abandoning the issue. Do every part that is not
blocked, then say in the issue and to the user exactly what you left and why. A
partially completed issue with a clear note beats a stalled one.

## Workflow

### 1. Validate before writing code

Cheapest possible win: the issue is already done, or no longer wanted.

```bash
gh issue view <N> --json number,title,body,labels,state,comments
```

Then look for it in the repo — `rg` for the feature, `git log -p -- <path>`,
`gh pr list --state merged --search "<keyword>"`. Issues outlive the code that
closed them.

Three outcomes:

- **Already implemented** — close it with a comment pointing at the commit, PR, or
  file that does it. This is a real completion, not a cop-out; say where the
  evidence is so the close is checkable.
- **Obsolete, duplicate, or explicitly deprioritised** (a `wont`/`wontfix`/
  `moscow:wont` label is the author telling you their own answer) — close it with
  the reasoning. Do not implement something the labels say nobody wants.
- **Live and wanted** — continue.

When the issue is large and the user has called it minor, the honest read is
usually that they want it *resolved*, not *built*. Scope it down to the smallest
thing that delivers the issue's actual intent, state the reduction in a comment,
and note what you deliberately left out. Shipping a quarter of an epic and saying
so is more useful than a half-built abstraction nobody asked for.

### 2. Decide the open questions

Minor issues are usually underspecified. For each gap, pick the option a careful
maintainer of *this* repo would pick, and prefer:

- the pattern already in the codebase over a better pattern that is new here
- the smallest change that satisfies the acceptance criteria
- boring and obvious over clever and general
- reversible over permanent

Write the decisions down as you make them — you will need them for the comment in
step 4, and reconstructing your reasoning afterwards is harder than noting it now.
A decision worth recording has a *rejected alternative*; if there was no real
alternative, it is an implementation detail, not a decision.

### 3. Implement

```bash
gh issue edit <N> --add-assignee @me
git checkout main && git pull
git checkout -b feature/<N>-short-description
```

Follow the repo's own conventions — read `CLAUDE.md`, match the surrounding code,
use the configured toolchain. Run the repo's quality gate before you believe
anything works, and run it again before the PR:

```bash
# whatever this repo actually uses
uv run pytest && uv run ruff check . && uv run ruff format --check .
```

Commit with the repo's message convention, referencing the issue.

### 4. Comment at milestones, not continuously

Issue comments are the progress record, and their value is inversely proportional
to how many there are. A reader wants two or three substantial comments, not
fourteen status pings.

Accumulate findings as you work and post when you reach something that changes
what a reader would understand — typically: after validation if the outcome was
surprising, after implementation, and at the merge. Each comment should answer:

- what I decided, and what I rejected
- what I found that the issue did not say (this is the most valuable part — it is
  knowledge the issue author did not have)
- what I verified, with the actual numbers
- what I did not do, and why

Prefer one comment that makes someone smarter over three that prove you were busy.
If nothing a reader needs has changed, post nothing.

### 5. PR, with a transcript

```bash
git push -u origin feature/<N>-short-description
gh pr create --title "#<N>: <what it does>" --assignee @me --body-file - <<'EOF'
Closes #<N>

## What this does
...

## Decisions
| Decision | Why | Rejected |
|---|---|---|

## Session transcript
What was tried, what failed, what that revealed. Dead ends included — they are
why the final shape is what it is.

## Verification
Commands run and their actual output.
EOF
```

The transcript is the part people skip writing and the part reviewers actually
use. Include the approaches that failed: a reviewer who knows you already tried
the obvious thing will not ask you to try it. Include short summary and conclusion, 1-2 sentences each.

### 6. Merge

Merge unless the invocation said `no-merge` (or "stop at PR", "don't merge",
"PR only") — then stop at the PR and say the link is waiting.

Read the *conclusion*, never the exit code. `gh pr checks --watch` can exit zero while
reporting `fail`, and chaining it with `&&` then merges a red build — which is easy to miss,
because the merge succeeding looks like the checks passing:

```bash
gh pr view <PR> --json statusCheckRollup --jq '[.statusCheckRollup[].conclusion]'
# only when that is SUCCESS:
gh pr merge <PR> --squash --delete-branch
```

After merging, check the default branch's own run too. A merge can be green per-PR and red
on `main` when another change landed in between.

Do not try to formally approve your own PR. GitHub rejects self-approval, and the
harness may block the attempt as well. That is not a reason to stop: if the branch
is mergeable and CI is green, merge and note in your summary that no approval
record exists. If branch protection genuinely requires a review, you cannot
satisfy it — say so, leave the PR open, and tell the user it needs their approval.

Then confirm the issue actually closed (`Closes #N` in the PR body does it
automatically; verify rather than assume) and sync local state.

## Contribution credit

The user wants this work on their contribution graph, and GitHub attributes a
commit to the account matching the **author** email. So:

- Never change `user.name`/`user.email`, and never pass `--author`. The repo's
  configured identity is the user's, and it is already correct.
- Verify once, early: `git config user.email` should be an email on their GitHub
  account. If it is not, the commits will not count — tell them, because this is
  invisible until the graph stays grey.
- `Co-Authored-By:` trailers are fine and do not take credit away from the author.
- Commits need to reach the **default branch** to count, which merging achieves.
  A PR left open does not count until merged.

## Batch mode

Given several issues, or "all the open ones", work in waves rather than one
enormous PR: group by theme so each PR is reviewable on its own, and handle the
closable ones (already done, obsolete, `wont`-labelled) as a first pass, since
they are pure subtraction and shrink the problem fast.

Report one consolidated summary at the end, not a play-by-play per issue. The user
asked for a backlog to disappear; they want the shape of what happened.

## Gotchas worth knowing

Hard-won, repo-agnostic, and each one costs real time to rediscover:

- **Commit subjects starting with `#`** (the `#123: fix: ...` convention) are
  silently stripped by any git operation using the default cleanup mode —
  `cherry-pick --continue`, `rebase --continue`, `commit --no-edit`. You get a
  commit whose first line is the body's first sentence. Prefix those commands with
  `git -c core.commentChar=';'`. `git commit -F file` is already safe.
- **Deleting a PR's base branch closes that PR**, and it cannot be reopened while
  the base is missing. When stacking PR B on PR A, merge A *without*
  `--delete-branch`, retarget B to `main`, then delete A's branch. If it already
  happened: push the base ref back, reopen, retarget, then delete.
- **`gh pr merge --squash`** produces one commit whose hash differs from the
  branch's, so a dependent branch must be rebased with the old commits dropped,
  not merged.
- **Self-approval is impossible** on your own PR — see step 6. Check
  `gh api repos/{owner}/{repo}/branches/main/protection` to learn whether a review
  is actually required before assuming you are stuck.
- **Pre-push hooks** that run the test suite will fire on every push including ref
  plumbing. Do not reach for `--no-verify` to silence a legitimately failing test;
  fix the test.
- **A green local suite is not a green build.** Windows and macOS are case-insensitive, so
  `Path.exists()` accepts a wrong-case path that Linux CI and GitHub's own file serving
  reject. Anything that touches paths — link checks, fixture loading, imports — can pass
  locally and fail in CI for this reason alone. When CI disagrees with your machine about a
  path, believe CI.
- **`Path.resolve()` hides case bugs.** On a case-insensitive filesystem it rewrites each
  component to the real on-disk spelling, so a check built on it passes when it should fail.
  Use `os.path.normpath` to collapse `..` and compare components against the real directory
  entries.

## Finishing

Tell the user, briefly: what shipped, what you decided for them, what you closed
without building and why, and anything you could not do. Lead with the things they
would disagree with — those are the only parts they need to read.
