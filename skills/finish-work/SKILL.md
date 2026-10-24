---
name: finish-work
description: "Take a pull request from \"I think I'm done\" to merged code on a verified, green main. Preflight the branch and worktree, rebase onto main, run the repo's own local gate, wait for CI on the head commit with a blocking watch, review in depth, require a formal APPROVE, merge only when approval and green CI are on the same head commit, then watch main, fix forward or revert, clean up branches, and report. Use when the user says finish this, land the PR, complete the PR, wrap this up, ship it, or merge on my behalf."
compatibility: Requires git and the gh CLI authenticated with pull-request, review, and merge access to the target repository.
---

# Finish work

Lands one pull request. The skill has one hard merge gate, applied even when
the repo's branch protection does not enforce it:

> **approval and green CI on the same head commit**

A review of another kind (a comment review, a chat message saying "looks good")
does not satisfy it, and neither does an approval given before the last push.
The commands that check the gate are in
[references/merge-gate.md](references/merge-gate.md).

**Status:** no end-to-end run with an approval yet. The first run, on
[pkuppens/skills#53](https://github.com/pkuppens/skills/pull/53) (the PR that
adds this skill), went through steps 0–4 and stopped at step 5: the agent's
`gh` login is the PR author, so it cannot approve its own PR, and #45 (bot
identity) is still open. That stop is the self-approval rule working as
intended.

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
pre-commit config, branch protection, allowed merge methods, merge queue.

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

### 5. Formal approval

A formal `APPROVE` review on the current head SHA, by the user or by the
agent. An agent approval states, in its body, the checks it ran and the SHA it
verified:

```bash
gh pr review <pr> --approve --body "Verified <sha>: <local gate>, CI <run>, review findings <fixed/filed>."
```

**Self-approval is impossible.** If the PR author equals the current `gh`
user (`gh api user --jq .login`), GitHub rejects the approval. Then:

1. use the bot flow from [#45](https://github.com/pkuppens/skills/issues/45)
   when it exists, so that the bot is the author and the user's login can
   approve; otherwise
2. leave the PR open and ask the user to approve it.

Never post a comment review instead and merge anyway. Never merge with an
admin override to get past a missing approval.

### 6. Merge gate

Merge only when all of these hold on **one** head SHA (check them with
[references/merge-gate.md](references/merge-gate.md)):

- an `APPROVE` whose `commit_id` is the head SHA, and no later
  `CHANGES_REQUESTED` from any reviewer;
- every required check `SUCCESS` on the head SHA;
- no unresolved review threads;
- the branch is up to date with the base (`mergeStateStatus` is not `BEHIND`).

Any push after the approval means another round of steps 3 and 5. Merge with
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
- Confirm the linked issue closed (`gh issue view <n> --json state`); if it did
  not, close it with a comment that points at the merge commit.
- Link the follow-up issues from step 4 on the issue.
- `clean-ci-runs` if it is installed.

### 9. Report

PR link, merge SHA, `main` run conclusion, follow-ups filed, iterations (fixes,
re-approvals after a push), and every step skipped with the reason.

## Stop and ask

Only in these cases. Everything else, decide and go on:

- a human has requested changes;
- CI is red and you cannot reproduce it within the timebox;
- a conflict changes behaviour on both sides;
- the gate would need an admin override, or the only possible approver is the
  PR author.
