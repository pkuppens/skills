---
name: dependabot
description: "Run the daily Dependabot check on your assigned PRs. Classify each bump by SemVer, treating 0.x minor bumps as major. Require green CI and a clean rebase. Run local review checks: lockfile, package usage, what CI ran. Post a formal GitHub review, not a plain comment. Approve and merge patch and minor bumps. Hold major bumps for a human, and merge them only when the user's invocation explicitly authorizes majors. Merge, watch the base branch, and revert through a PR if it goes red. Use for the daily dependency check, or to review, triage, update or clear Dependabot PRs, including an explicit \"update majors\" request."
compatibility: Requires the gh CLI authenticated with read, pull-request-review, and merge access to the target repository, plus Python 3.9+ for scripts/classify_bump.py. The Step 5a review checks also need git, a local clone of the target repository, and that ecosystem's toolchain (for example uv or npm); without them, the local checks are recorded as not run.
allowed-tools: Bash(gh pr *) Bash(gh run *) Bash(gh repo view*) Bash(gh api*) Bash(git *) Bash(uv *) Bash(npm view*) Bash(npm explain*) Bash(npm ls*) Bash(curl -s https://pypi.org/*)
---

# Dependabot daily check

Reviews the Dependabot PRs assigned to you and posts a **formal GitHub
review** for each — `gh pr review`, which counts as a review contribution —
never a bare `gh pr comment`. PRs that clear all three gates (version, CI,
rebase; a major bump clears the version gate only when the user explicitly
authorized majors, Step 6) and the review checks (Step 5a) are merged with the
repository's allowed strategy (Step 0, Step 8), and the resulting
base-branch run is watched to a
conclusion. With no blocker (Step 7) it runs end to end without pausing for
a go-ahead. This skill only ever identifies, reviews, merges, and — when a
merge turns the base branch red — reverts that merge through a PR (Step 9):
never edit source, test, or config files to chase a green build — investigate
and report the finding instead (Step 5).

If invoked with a repo (`owner/name`) or a PR number, use it as the target.
Otherwise default to the current directory's repo (`gh repo view --json
nameWithOwner`).

## Steps

### 0. Detect the project policy and the invocation

Once per repository, before Step 1: read the allowed merge methods, the
required CI check, and the project's dependency policy. Project rules only make
the skill stricter. **Majors are merged only when the user's invocation
explicitly authorizes them** (for example "update majors on green CI, I
pre-checked"); "run the daily check" does not. When unsure, majors hold.
Commands and rules: [references/project-policy.md](references/project-policy.md).

### 1. Find the Dependabot PRs assigned to you

```bash
gh pr list --repo <repo> --state open --assignee @me \
  --json number,title,author,url,createdAt,labels,headRefName --limit 100
```

A PR counts as Dependabot-authored when any of these holds — check all
three, since each fails in a different environment:

- `author.is_bot` is `true` **and** `author.login` contains `dependabot`
  (observed as `app/dependabot`) — the reliable signal;
- the PR carries a `dependencies` label — Dependabot's default;
- `headRefName` starts with `dependabot/` — survives even when author
  metadata is rewritten by a mirror or a rebase bot.

Title prefixes (`chore(deps`, `chore(deps-dev`, `build(deps`) are a last
resort: humans use them too, so they confirm nothing on their own.

Dependabot does not assign anyone itself. An empty result usually means
assignment was never configured, not that there is nothing to do — say so
plainly and point at `assignees:` in `.github/dependabot.yml` (or whatever
automation the repo uses) rather than silently widening the search. Only
fall back to every open Dependabot PR (drop `--assignee @me`) when the user
asks for that, and report which set you actually used.

**Done when:** the PRs in scope are listed with the signal that identified
each one, and anything excluded is named with its reason — a user-named PR
that turns out not to be Dependabot-authored included.

### 2. Classify each bump's severity and gate verdict

Trust SemVer for the verdict. Do not review upstream code to decide it.
The PR diff is read only for version numbers: the manifest and lock lines.
To learn what changed, read in this order and stop at the first that answers:
the release notes (patch notes) in the PR body, the package's CHANGELOG, then
the commit log between the two tags (`gh api repos/<o>/<r>/compare/<old>...<new>`
or `git log <old>..<new>`). Never read the source diff of the dependency:
too much effort, and not needed for a verdict.

Run [scripts/classify_bump.py](scripts/classify_bump.py) (resolve the path
relative to this skill's own directory) against the PR's diff **and** its
body:

```bash
gh pr diff <number> --repo <repo> > /tmp/pr.diff
gh pr view <number> --repo <repo> --json body --jq .body > /tmp/pr.body
python scripts/classify_bump.py /tmp/pr.diff --body /tmp/pr.body \
  --manifest package.json --manifest pyproject.toml   # the manifests the repo has
```

`--manifest` tags each package `direct` or `indirect` and prints `MAJOR-USE:`.
Judge every package against the cooldown by its own severity, the worst
outcome decides ([major-bumps.md M1](references/major-bumps.md#m1--cooldown)).

It parses every `"pkg": "old"` → `"pkg": "new"` pair and compares versions
as numeric tuples — never lexicographically, so `1.9.0` → `1.11.0` reads as
minor, not a downgrade. It prints a per-package severity, an `OVERALL:`
(the worst across the PR — one major package makes a whole group major), a
`GATE:` verdict of `AUTO` or `HOLD` applying the rule below, and any
`WARN:` lines.

Always pass `--body` on a group PR: lock-only updates are missing from the
diff. Read every `WARN:` line, and hold on a count mismatch or a `conflict`
row. When it prints `NO_VERSION_CHANGES_FOUND`, parse the title by hand and
treat an unpinnable pair as `unclassifiable` (holds). Why, and the details:
[references/classifier-notes.md](references/classifier-notes.md).

#### The version rule

A bump is auto-mergeable only when the **breaking component is unchanged**
and the new version is an overall increase. The breaking component is the
leftmost non-zero one. SemVer 2.0.0 (item 4) says that while the major is `0`,
anything may change at any time, and does not say more. This skill follows the
npm caret and Cargo reading, the strictest common one:

- `X.Y.Z` with `X > 0`: a change of `X` is major, of `Y` minor, of `Z` patch.
- `0.Y.Z` with `Y > 0`: a change of `Y` is **major**. Only `Z` is patch.
- `0.0.Z`: any change is **major**. `^0.0.1` admits no other version.

| From | To | Verdict | Why |
|---|---|---|---|
| `1.2.3` | `1.3.0` | AUTO | minor increase |
| `1.2.3` | `1.2.4` | AUTO | patch increase |
| `1.2.3` | `1.3.1` | AUTO | minor increase; the lower patch is a normal reset |
| `1.2.3` | `1.1.0` | HOLD | minor decrease |
| `1.2.3` | `1.2.1` | HOLD | patch decrease |
| `1.2.3` | `2.0.0` | HOLD | major bump (held unless the invocation authorizes majors, Step 0) |
| `0.1.2` | `0.1.5` | AUTO | patch inside the same `0.Y` line |
| `0.1.2` | `0.2.0` | HOLD | major: `0.Y` minor bump may break |
| `0.9.0` | `0.10.0` | HOLD | major, same reason |
| `0.0.1` | `0.0.2` | HOLD | major: every `0.0.Z` release may break |
| `0.9.0` | `1.0.0` | HOLD | major |

Comparing the version tuples as a whole is what makes the `1.3.1` row come
out right — checking each component in isolation would wrongly read the
reset patch digit as a decrease. `python scripts/classify_bump.py
--self-test` asserts every row here, so the rule is verified by running it
rather than by re-reading this table; run it if you change the gate.

**GitHub Actions tags (`@v5` → `@v7`)** have no minor or patch. The
classifier reports severity `tag`, gate `AUTO` for an increase, and CI is the
real check. Before approving one, check that the touched workflow runs on pull
requests. Single-level versions that are not Actions (Docker, calver) hold.
See [references/classifier-notes.md](references/classifier-notes.md).

**Done when:** every PR in scope has a severity and an AUTO/HOLD verdict
backed by the specific old→new pair(s), not a guess from the title.

### 3. Check CI

```bash
gh pr checks <number> --repo <repo>
```

Classify as **green** (every check succeeded), **red** (any failed),
**pending**, or **none** (no workflow ran at all — distinct from green;
don't treat silence as success).

### 4. Check the rebase is clean

The merge must be a *direct* rebase with no conflict resolution, so confirm
GitHub has computed mergeability and likes it:

```bash
gh pr view <number> --repo <repo> --json mergeable,mergeStateStatus
```

| `mergeable` / `mergeStateStatus` | Meaning | Action |
|---|---|---|
| `MERGEABLE` / `CLEAN` | rebases cleanly, checks pass | eligible to merge |
| `MERGEABLE` / `BEHIND` | no conflicts, just behind base | eligible — a rebase merge replays onto base, which is exactly what `BEHIND` needs |
| `MERGEABLE` / `BLOCKED` | branch protection unsatisfied (e.g. this very review is the missing approval) | re-check after posting the approval; if still blocked, leave it and say which rule blocks |
| `CONFLICTING` / `DIRTY` | real conflicts | never merge — hold, and say Dependabot should rebase it (`@dependabot rebase`) |
| `UNKNOWN` | GitHub hasn't computed it yet | not a rejection — wait a few seconds and re-poll once or twice before treating it as unknown-and-held |

`UNKNOWN` is the easy one to get wrong: it appears routinely on
freshly-pushed branches, and reading it as "not mergeable" would hold
perfectly good PRs every morning.

**Done when:** every PR has one of those states recorded, with `UNKNOWN`
re-polled rather than taken at face value.

### 5. Investigate red or missing CI (skip if green)

Never edit files to fix it. Find out why, for the comment: compare with the
base branch's latest run (a same failure there predates this PR), rerun a
stale base run, skim `gh run view <run-id> --log-failed`, and rerun a failed
job once to spot a flake. A green base run only counts if it is recent.
Details: [references/classifier-notes.md](references/classifier-notes.md#red-or-missing-ci).

### 5a. Run the review checks (always, for PRs still eligible)

Green CI says the checks passed, not what they tested. First run
`git fetch origin <base>`: a stale local base ref makes `git diff
origin/<base>...HEAD` show changes from earlier merges, and a patch can look
like a major bump (seen on pkuppens.github.io#133). For every PR that is
still AUTO, green and rebase-clean, and for every major bump that is green and
rebase-clean and is a major (Step 6), run R1–R6 from
[references/review-checks.md](references/review-checks.md). Run them in a
throwaway worktree, in a container where you can, because R3 and R6
execute the new dependency's code and clearing the token variables does not
hide your other credentials (Safety section of the reference). R7, the base-branch evidence, runs once
in Step 7.

**Done when:** each eligible PR has a hold, note, or pass result for R1–R6,
with the commands that were run.

### 6. Decide

All three gates must pass, and no Step 5a check may hold. Any failure
holds the PR:

| Gate verdict | CI | Rebase | Verdict |
|---|---|---|---|
| AUTO (patch, minor, or Actions `tag`) | green | clean (`CLEAN`/`BEHIND`) | **Approve + merge** (Template A), if no Step 5a check holds |
| AUTO, patch or `tag` package still in cooldown (worst in the group) | green | clean | **Approve + merge** (Template A) with the cooldown notice in the Explanation, if no Step 5a check holds |
| AUTO, minor package still in cooldown (worst in the group) | green | clean | **Comment** (Template B, cooldown variant): ask for a human look, list the release notes to read. Never merge |
| HOLD — major, **every** major indirect, parents unchanged or minor/patch | green | clean | **Approve + merge** (Template A, indirect-major variant) under the rule in [references/major-bumps.md](references/major-bumps.md#indirect-major-rule), when R1–R6 pass and the cooldown is met. A parent with a major bump, or a forced override, takes the next row |
| AUTO, but a Step 5a check holds | green | clean (`CLEAN`/`BEHIND`) | **Comment**, hold (Template B, review-check variant), naming the check and the finding |
| AUTO | green | `DIRTY`/`UNKNOWN` after re-poll | **Comment**, hold (Template D) |
| HOLD — major, **not** authorized, a major is direct or its parent has a major bump, or its cooldown is not met | green | clean | **Comment**, hold (Template B, major variant; cooldown variant names the date it matures) with the evidence from [references/major-bumps.md](references/major-bumps.md) (M1–M4, R1–R6) as advice for the human. Never approve or merge. The human decides |
| HOLD — major, **authorized** by the invocation (Step 0) | green | clean | **Approve + merge** (Template A, major variant) if no Step 5a check holds (R1, R2). The authorization replaces the M1–M4 conditions, but run and report them anyway. Docker, runtime, calver and project-policy tool-dependency bumps are covered only when the invocation names them |
| HOLD — major | red, pending, none, or not clean | any | **Comment**, hold (Template B, or C/D for the CI or rebase cause) — a major (or a single-level non-Action version) needs green CI and a clean rebase before it can be considered at all |
| HOLD — downgrade | any | any | **Comment**, hold (Template B) — a version going backwards is never an expected Dependabot bump |
| HOLD — unchanged | any | any | **Comment**, hold (Template B) — nothing effective to approve |
| HOLD — conflict | any | any | **Comment**, hold (Template B) — the manifest diff and the PR body disagree about a version, so the real change is unclear |
| HOLD — unclassifiable | any | any | **Comment**, hold (Template B) |
| AUTO with a count-mismatch `WARN:` | any | any | **Comment**, hold (Template B) — the package list in an approval would be incomplete |
| any | red or none | any | **Comment** with the Step 5 finding (Template C) |

Every severity `classify_bump.py` can emit has a row here; if you extend the
classifier, extend this table in the same change.

Templates: [references/review-templates.md](references/review-templates.md).

### 7. Show the plan, then proceed unless something blocks

Before any `gh pr review` or `gh pr merge` call, print a table of every PR in
scope with its package(s), severity, gate verdict, CI status, rebase state,
review-check result (Step 5a), and proposed action — stating explicitly which ones will be merged.

Then record the base branch's current state, the baseline Step 9 compares
against:

```bash
git ls-remote origin refs/heads/<base>        # pre-merge base SHA
gh run list --repo <repo> --branch <base> --limit 5 \
  --json databaseId,headSha,workflowName,status,conclusion
```

**The default is to go ahead**: post the reviews and merge without waiting
for the user. The gates and review checks in Steps 2–6 are what make that safe, and Step 9
catches the rest. Two things change that:

- **Base branch red → no merges.** If the base branch's latest completed
  run of a CI workflow is `failure` (including a fresh rerun from Step 5),
  skip every merge and ask before merging anything: on a red base a
  post-merge failure can't be attributed, and the revert in Step 9 depends
  on that attribution. Reviews and hold comments still post. A green run on
  an *older* base SHA is not evidence. Run R7 from
  [references/review-checks.md](references/review-checks.md): dispatch the
  workflow on the current base SHA and wait for the result.
- **The user asked to confirm first**, for this run or in standing
  instructions → pause before posting anything.

A held PR (Templates B/C/D) is not a blocker: posting its comment is the
routine outcome, and it proceeds with the rest. `skipped` and `success` on
the base branch both count as not red.

### 8. Post the reviews, merge the eligible ones

```bash
gh pr review <number> --repo <repo> --approve --body "..."   # Template A
gh pr review <number> --repo <repo> --comment  --body "..."  # Template B/C/D
```

Never `--request-changes` — the point of Templates B/C/D is to flag for a
human decision, not block the PR.

Templates A and B include the Evidence table, and line comments on the lock
entries are optional. See
[references/review-templates.md](references/review-templates.md).

For every PR approved under Template A, follow the approval with a merge
using the strategy from Step 0. Squash, authored by you, is the default:

```bash
gh pr merge <number> --repo <repo> --squash --delete-branch \
  --author-email "$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')" \
  --match-head-commit <reviewed-head-sha>
```

`--match-head-commit` makes sure the merged commit is the one you reviewed.
If Dependabot pushed in the meantime, the merge fails: review again.

**Merge strategy and cleanup.** Squash, with your noreply address as the
commit author, so the merge counts as your commit and you are the first
contact when it breaks. Use rebase only when the repo disallows squash
(the commit then stays Dependabot's), and drop `--author-email`. Never a merge
commit unless it is the only strategy allowed. After the merges, remove leftover `dependabot/*` branches that have
no open PR. Details and commands:
[references/merge-and-cleanup.md](references/merge-and-cleanup.md).

**Auto-merge.** Dependabot PRs do not merge themselves. Only a repo that
turns on GitHub auto-merge for the PR does (a workflow running `gh pr merge
--auto`, or a person clicking it). Before merging, check `gh pr view <number>
--json autoMergeRequest`. When it is set, GitHub merges the PR once required
checks pass, with no review by this skill. Still post the review, do not merge
yourself, and say so in the report. Do not trust a workflow's file name:
`autoMergeRequest` is the signal. babblr's `dependabot-automerge.yml` is named
for auto-merge but only prints a message and merges nothing.

Re-check mergeability right before merging if the approval was what unblocked
it (`BLOCKED` in Step 4). If the merge is refused, skip it, say why, and
leave the approval for a human.

**Done when:** every PR in scope has either a posted review (and, for
Template A, a merge attempt) or an explicit "skipped: `<reason>`" line in the
final report — none silently dropped.

### 9. Babysit the result

A merge is not done when the API returns 200 — it's done when the base
branch is still green. For each merged PR:

```bash
gh pr view <number> --repo <repo> --json state,mergedAt,mergeCommit
gh run list --repo <repo> --branch <base> --limit 1 --json databaseId,status,conclusion
gh run watch <run-id> --repo <repo> --exit-status
```

Confirm `state` is `MERGED` (a 200 on an auto-merge queue means *queued*, not
merged), then watch the base-branch run it triggered to a terminal
conclusion. If several PRs merged in one pass, watch the run after the last
one — it contains all of them.

#### If the base branch goes red: revert

Report it immediately and prominently, with the failing job and the merge
commit, then start reverting — don't wait to be asked. Do **not** push a fix
to the base branch to chase green: that converts a clean, revertible
dependency merge into an unreviewed direct commit on a protected branch.

In short: rerun once to rule out flake, match base runs to merge commits by
`headSha` to find the culprit, revert it through a PR, merge the revert once
its CI is green. Then analyse why it failed and post Template E, with a
recommendation, on the original PR. The full procedure, commands included, is
in [references/revert-procedure.md](references/revert-procedure.md).

### 10. Report

**You are the first contact.** A merge by this skill is yours: it is authored
by you and the review is under your login. When anything goes wrong (a red
base run, a revert, a merge that was refused or held), assign the revert PR or
issue to `@me` and put it first in the report, so GitHub notifies you and you
can refine the skill from it.

Summarize: how many approved and merged, how many approved but left unmerged
(and why), how many held (and which gate or review check held them), how many needed CI
investigation (and the finding), the post-merge base-branch status, and any
revert PR with its state. Link each PR.

## Notes

A Claude Code-specific variant of this skill, kept locally at
`~/.claude/skills/dependabot/` and not part of this portable copy, layers
`disable-model-invocation: true` (only fires on deliberate `/dependabot`,
never auto-invoked), `disallowed-tools: Edit Write NotebookEdit` (a
tool-level guardrail backing up the "never edit files" instruction above),
and named `repo`/`pr_number` arguments on top. Those fields aren't part of
the Agent Skills spec this repo's `skills-ref` validates, so they can't
travel with the portable copy — this copy relies on Step 7's blocker list
and the body's instructions for the same safety properties on every host
(Cursor, Codex, Claude).

## Examples

Earlier sessions, and the rule each one supports. Add a row after each real
run. A rule with no row is a hypothesis, not policy.

| Session | Repo and PR | Outcome | Rule it supports |
|---|---|---|---|
| Merge path | [pkuppens.github.io #124](https://github.com/pkuppens/pkuppens.github.io/pull/124), [#125](https://github.com/pkuppens/pkuppens.github.io/pull/125) | merged, base green | Patch/minor bump with green CI and a clean rebase: approve and merge. |
| Red CI before the PR | [babblr #341](https://github.com/pkuppens/babblr/pull/341), [#342](https://github.com/pkuppens/babblr/pull/342), [#343](https://github.com/pkuppens/babblr/pull/343) | held, comment only | A failure that also occurs on the base branch is not the bump's fault. Report it, do not merge on red. |
| Lockfile-only patch | `uv` lockfile patch PR, see [#87](https://github.com/pkuppens/skills/issues/87), [#88](https://github.com/pkuppens/skills/pull/88) | approved with two notes | Green CI is not enough: check the lockfile and the usage (R1-R6). |
| Dev-dependency major, aged (before Step 0; now needs explicit authorization) | [pkuppens.github.io #132](https://github.com/pkuppens/pkuppens.github.io/pull/132) (jsdom 30 to 31) | merged | R4/R5 found three Node scripts CI did not run; R6 ran them locally. |
| Major path, cooldown met (before Step 0; now needs explicit authorization) | [babblr #365](https://github.com/pkuppens/babblr/pull/365) (jsdom 30.1.3 to 31.0.0 plus 12) | approved and merged | Evidence for a major: 7-day cooldown, mapped usage, coverage. Now merged only on explicit authorization. |
| Major path, cooldown not met | [babblr #369](https://github.com/pkuppens/babblr/pull/369) (same group) | held | Five versions were under 7 days old: the group waits as a whole. |
| Full run, dev-dependency group | [pkuppens.github.io #133](https://github.com/pkuppens/pkuppens.github.io/pull/133) (8 updates, minor) | approved, rebase-merged, `main` deploy run green | R1-R7, review, merge, babysit and branch check all ran through the skill. A stale local base ref once faked a major (Step 5a now fetches first). |
| Revert path | rehearsed in scratch clones only, [#52](https://github.com/pkuppens/skills/pull/52), [#92](https://github.com/pkuppens/skills/issues/92) | range revert, newest first, restores the files | The git mechanics work. A real red base run has not happened, so the analyse-and-recommend step is unproven. |
| Cooldown by severity, dry run of the classifier only | [babblr #373](https://github.com/pkuppens/babblr/pull/373) (jest-dom 8.0.0 plus minors and patches) | expected: review advice, not a hold | Major old enough, minors too young: the worst package decides, and a young minor gets review advice. No comment was posted from the new templates yet. |

The review checks (Step 5a) and the major path ran by hand, not yet end to
end through the skill ([#90](https://github.com/pkuppens/skills/issues/90)).
Treat both as experimental. Step 0 and the authorized-major path
([#101](https://github.com/pkuppens/skills/issues/101)) have not run on a real PR.
