---
name: finish-work
description: "Take a pull request from \"I think I'm done\" to merged code on a verified, green main. Preflight the branch and worktree, rebase onto main, run the repo's own local gate, wait for CI on the head commit with a blocking watch, review in depth, require the approval the repo enforces (or, where none is enforced, the user's explicit instruction to merge), merge only when that sign-off and green CI are on the same head commit, then watch main, fix forward or revert, clean up branches, and report. Use when the user says finish this, land the PR, complete the PR, wrap this up, ship it, or merge on my behalf."
compatibility: Requires git and the gh CLI authenticated with pull-request, review, and merge access to the target repository.
---

# Finish work

Lands one pull request. The skill has one hard merge gate, applied even when
the repo's branch protection does not enforce CI:

> **green CI on the head commit, and the sign-off the repo calls for**

What counts as sign-off depends on whether the repo **enforces** an approving
review (branch protection or a ruleset requires one, or the probe in
[references/merge-gate.md](references/merge-gate.md#0-is-an-approval-enforced)
cannot tell):

- **Enforced:** a formal `APPROVE` on the head commit, by the user or, after
  the chores, by the agent (step 5). Never an admin override.
- **Not enforced** (zero required reviews, or no protection): no approval is
  needed, because GitHub would not ask for one either. The user's plain-words
  instruction to land this PR is the sign-off (step 5). A bare "ok" is not one.

Nothing the agent posted counts as either. The commands that check the gate
are in [references/merge-gate.md](references/merge-gate.md).

If invoked with a PR number or URL, use it. Otherwise use the PR for the
current branch (`gh pr view --json number`), and create one in step 0 if none
exists.

## Hand off first

- **Dependabot PRs** (bot author, `dependencies` label, or a `dependabot/`
  branch) go to [dependabot](../dependabot/SKILL.md). It already has the
  severity classification, rebase gate, review templates, rebase-merge,
  base-branch watch and revert procedure for them. Do not run them through
  this skill as well.
- **Merge conflicts** in step 1 go to `resolving-merge-conflicts` when it is
  installed; otherwise resolve them by hand and say what each side wanted.

## Steps

### 0. Preflight

Check that you are about to work on the right thing, before changing anything:

- the repo (`gh repo view --json nameWithOwner`), the branch (`git branch
  --show-current`) and the worktree (`git worktree list`) match the PR's
  `headRefName`;
- the working tree is clean (`git status --porcelain` is empty);
- no other session is working in the same folder: a recent `.git/index.lock`,
  or a branch you did not expect, means stop and ask;
- a PR exists; if not, create it (`gh pr create --assignee @me`, with
  `Closes #N` in the body);
- the linked issue is known (`gh pr view --json closingIssuesReferences`).

Then read what the repo has, because later steps depend on it — see
[references/repo-facts.md](references/repo-facts.md): CI workflows, a
pre-commit config, branch protection, allowed merge methods, merge queue, and
whether an approving review is enforced (decides step 5). Note the user's
wording at invocation.

### 1. Sync

```bash
git fetch origin
git rebase origin/<base>
git push --force-with-lease
```

On conflicts: resolve, `git -c core.commentChar=';' rebase --continue` (a
`#123:` subject line is otherwise stripped as a comment), then go through
step 2 again. **Stop and ask** when a conflict changes behaviour on both sides.

### 2. Local gate

Run the repo's own gate before spending CI time. Use only what the repo has:

| The repo has | Run |
|---|---|
| `.pre-commit-config.yaml` | `pre-commit run --all-files` |
| a test suite | its documented test command (`uv run pytest`, `npm test`, …) |
| a lint/format config | its lint command |
| none of these | say so; step 3 is then the only gate |

**No pre-commit config:** run the test and lint commands directly; do not
install or add pre-commit here. **No CI** (no workflow runs on the PR): this
step becomes mandatory and its output goes in the report, since nothing else
will check the change.

### 3. CI on the head commit

Wait with a blocking watch, never a polling loop:

```bash
gh pr checks <pr> --watch --fail-fast
gh pr view <pr> --json headRefOid,statusCheckRollup
```

Read the conclusions, not the exit code: `gh pr checks --watch` can exit 0
while a check failed. Every check must be `SUCCESS` (or `SKIPPED`/`NEUTRAL`)
and must belong to the current `headRefOid`.

Red: reproduce the failure locally first, fix it, commit, and go back to
step 2. CI red and not reproducible within about 30 minutes → **stop and
ask**. No checks at all on a repo that has workflows is not green: find out
why (path filters, a disabled workflow) before going on.

### 4. Review

- Run an in-depth review: [brutally-honest-code-review](../brutally-honest-code-review/SKILL.md),
  or `code-review` when installed.
- Read every open human review comment and thread:
  `gh pr view <pr> --json reviews,comments` and the review threads query in
  [references/merge-gate.md](references/merge-gate.md).

Sort findings into two groups, the way
[Google's reviewer standard](https://google.github.io/eng-practices/review/reviewer/standard.html)
does: a change that improves overall code health is approvable even when it is
not perfect.

- **Blocking** (wrong behaviour, missing test for new logic, broken
  docs/links): fix it, and every fix goes back through steps 2–3.
- **Non-blocking**: file a follow-up issue, link it on the PR, and go on.

A human who has **requested changes** → **stop and ask**. Do not dismiss
their review.

### 5. Sign-off

Run the probe in [references/merge-gate.md](references/merge-gate.md#0-is-an-approval-enforced).
It gives the required-review counts for protection and rulesets; both `0` is
not enforced, and anything unreadable (`unknown`) is treated as enforced.

**Not enforced.** No approval is required and none is requested. The sign-off
is the user's instruction to land this PR in plain words ("merge it", "ship it",
"merge on my behalf"; a bare "ok" or "go" is not one), or a user comment review
on the head SHA that clearly says to merge. It covers the commits **this run**
adds in steps 1-4 (sync, fixes to blocking findings). A commit by anyone else
after the instruction needs a new one. If the user only asked to prepare or
review, stop at "ready to merge" and ask. Before merging, post the sign-off as a
marked PR comment on the head SHA that quotes the words, so the record is on
the PR. The review in step 4 still runs: only the formal approval is dropped.

**Enforced.** A formal `APPROVE` review on the current head SHA, by the user or
by the agent. An agent approval states, in its body, the checks it ran and the
SHA it verified:

```bash
gh pr review <pr> --approve --body "Verified <sha>: <local gate>, CI <run>, review findings <fixed/filed>."
```

**Self-approval is impossible.** If the PR author equals the current `gh`
user (`gh api user --jq .login`), GitHub rejects the approval, and a comment
review does not satisfy a required-review rule either. Then use the bot flow
from [#45](https://github.com/pkuppens/skills/issues/45) when it exists (the
bot is the author, so the user's login can approve), or another approver;
otherwise post the step-4 findings and verified SHA as a PR comment and tell the
user the repo needs an approval this session cannot give. Never use an admin
override.

**An approval on an older head carries over** when the stable patch-id of the
PR's own diff is the same at the approved SHA and at the head (a rebase, or the
base merged into the branch); the check is in
[references/merge-gate.md](references/merge-gate.md#carrying-an-approval-over-a-trivial-rebase).
Only the approval carries: CI on the new head is still required. Say in the
report that it was carried, with both SHAs. A different patch-id, an
unfetchable old SHA, or a `CHANGES_REQUESTED` review means re-approve.

The agent and the user share one login, so every comment or review the agent
posts ends with the marker `<!-- finish-work:agent -->`, and anything with that
marker never counts as sign-off. The agent never posts a comment review meant
as an approval. A review that asks a question, requests a change, or reads as
mixed is not a go-ahead: ask the user.

### 6. Merge gate

Merge only when all of these hold on **one** head SHA (check them with
[references/merge-gate.md](references/merge-gate.md)):

- the sign-off from step 5: where approval is enforced, an `APPROVE` whose
  `commit_id` is the head SHA; where it is not, the user's recorded
  instruction to land. Either way, no later `CHANGES_REQUESTED` from any
  reviewer;
- every required check `SUCCESS` on the head SHA;
- no unresolved review threads;
- the branch is up to date with the base (`mergeStateStatus` is not `BEHIND`).

Any push after the sign-off means another round of steps 3 and 5, unless it
carries over or is covered by the instruction (step 5). Merge with
the repo's allowed method, preferring rebase-merge, then squash:

```bash
gh pr merge <pr> --rebase --delete-branch --match-head-commit <sha>
```

`--match-head-commit` makes GitHub refuse the merge if the head moved after
the gate was checked. With a merge queue, use `gh pr merge <pr> --auto`
instead and confirm `state` becomes `MERGED`, since a queued PR is not yet
merged. A gate that could only pass with an admin override → **stop and ask**.

### 7. Watch main

```bash
gh pr view <pr> --json state,mergeCommit
gh run list --branch <base> --commit <merge-sha> --json databaseId,workflowName,status,conclusion
gh run watch <run-id> --exit-status
```

A merge can be green on the PR and red on `main` when another change landed in
between. If `main` goes red:

- **cause clear** → a fix-forward PR;
- **cause unclear** → a revert PR (`git revert <merge-sha>` on a new branch).

Both go through this same skill from step 0. Never push a fix straight to
`main`. The revert procedure in
[dependabot/references/revert-procedure.md](../dependabot/references/revert-procedure.md)
also applies here.

### 8. Cleanup

- [branch-cleanup](../branch-cleanup/SKILL.md) for the local and remote branch.
  Run it with `--execute` straight after the merge, without asking. `gh pr merge
  --delete-branch` can leave the local branch behind (a worktree holds it, or a
  rebase merge made it look unmerged); this step removes it.
- Confirm the linked issue closed (`gh issue view <n> --json state`); if it did
  not, close it with a comment that points at the merge commit.
- Link the follow-up issues from step 4 on the issue.
- `clean-ci-runs` if it is installed.

### 9. Report

PR link, merge SHA, `main` run conclusion, follow-ups filed, iterations (fixes,
re-approvals after a push), and every step skipped with the reason.

## Examples

Real runs: [#53](https://github.com/pkuppens/skills/pull/53) (the PR that added
this skill) and #65/#71. Each went through steps 0–4 and stopped at step 5,
because the agent's login is the PR author and cannot approve (#45, bot
identity, is open). The user then merged by hand (`6365ee4`; `fa03d48`,
`3670df8`). Steps 7–8 ran afterwards on the first run; the second caught
approvals left on SHAs the user had since rebased, which the carry-over rule
([#76](https://github.com/pkuppens/skills/issues/76)) now covers. The
carry-over itself and steps 5–6 (the agent running the merge) have not run end
to end.

## Stop and ask

Only in these cases. Everything else, decide and go on:

- a human has requested changes;
- CI is red and you cannot reproduce it within the timebox;
- a conflict changes behaviour on both sides;
- the gate would need an admin override;
- approval is enforced and missing, and the agent's own login is the PR author
  (nobody here can approve it);
- approval is not enforced and the user has not said to land the PR.
