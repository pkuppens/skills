---
name: dependabot
description: Run the daily Dependabot check — find the open Dependabot PRs assigned to you (by bot author, dependencies label, or dependabot/** branch), classify each version bump as patch/minor/major from the diff rather than the title, require green CI and a clean no-conflict rebase, post a formal GitHub review (not a plain comment) approving only same-major increases, rebase-merge those, then babysit the base branch run afterwards. Use when the user wants their daily or routine dependency check, or wants to review, triage, clear out, or work through Dependabot PRs, dependency-update PRs, or version-bump PRs.
compatibility: Requires the gh CLI authenticated with read, pull-request-review, and merge access to the target repository, plus Python 3.9+ for scripts/classify_bump.py.
allowed-tools: Bash(gh pr list*) Bash(gh pr view*) Bash(gh pr diff*) Bash(gh pr checks*) Bash(gh run list*) Bash(gh run view*) Bash(gh run watch*) Bash(gh repo view*) Bash(gh api*)
---

# Dependabot daily check

Reviews the Dependabot PRs assigned to you and posts a **formal GitHub
review** for each — `gh pr review`, which counts as a review contribution —
never a bare `gh pr comment`. PRs that clear all three gates (version, CI,
rebase) are rebase-merged, and the resulting base-branch run is watched to a
conclusion. This skill only ever identifies, reviews, and merges: never edit
source, test, or config files to chase a green build — investigate and report
the finding instead (Step 5).

If invoked with a repo (`owner/name`) or a PR number, use it as the target.
Otherwise default to the current directory's repo (`gh repo view --json
nameWithOwner`).

## Steps

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

Run [scripts/classify_bump.py](scripts/classify_bump.py) (resolve the path
relative to this skill's own directory) against the PR's diff **and** its
body:

```bash
gh pr diff <number> --repo <repo> > /tmp/pr.diff
gh pr view <number> --repo <repo> --json body --jq .body > /tmp/pr.body
python scripts/classify_bump.py /tmp/pr.diff --body /tmp/pr.body
```

It parses every `"pkg": "old"` → `"pkg": "new"` pair and compares versions
as numeric tuples — never lexicographically, so `1.9.0` → `1.11.0` reads as
minor, not a downgrade. It prints a per-package severity, an `OVERALL:`
(the worst across the PR — one major package makes a whole group major), a
`GATE:` verdict of `AUTO` or `HOLD` applying the rule below, and any
`WARN:` lines.

**Always pass `--body` on a group PR.** When a package's existing range
already covers the new version (`^5.0.2` covering `5.0.3`), Dependabot
updates only the lock file and the manifest diff shows nothing for it — so
the diff alone silently under-reports. The body's `Updates \`pkg\` from X to
Y` lines come from Dependabot's update metadata, so reconciling against them
recovers those packages (tagged `[lock-only]`) without parsing the lock file.
This matters because the templates promise a concrete package list: an
approval naming 2 of 3 bumped packages is a misleading review, even when the
verdict happens to be right.

Read the `WARN:` lines rather than skimming past them. A count mismatch
against the body's "with N updates" claim, or a `conflict` row where the
manifest and the body disagree about a version, means the package list you
are about to put in a review is not trustworthy — hold instead of guessing
which source is right.

If it prints `NO_VERSION_CHANGES_FOUND` (non-npm ecosystem, or neither
source yields a pair), parse the PR title's "from X to Y" wording by hand and
apply the same rule — treating anything you can't pin to a concrete old→new
pair as `unclassifiable`, which holds.

#### The version rule

A bump is auto-mergeable only when the **major component is unchanged** and
the new version is an **overall semver increase**. From `1.2.3`:

| New version | Verdict | Why |
|---|---|---|
| `1.3.0` | AUTO | minor increase |
| `1.2.4` | AUTO | patch increase |
| `1.3.1` | AUTO | minor increase; the lower patch number is a normal reset on a minor bump, not a decrease |
| `1.1.0` | HOLD | minor decrease |
| `1.2.1` | HOLD | patch decrease |
| `2.0.0` | HOLD | major bump |

Comparing the version tuples as a whole is what makes the `1.3.1` row come
out right — checking each component in isolation would wrongly read the
reset patch digit as a decrease. `python scripts/classify_bump.py
--self-test` asserts every row here, so the rule is verified by running it
rather than by re-reading this table; run it if you change the gate.

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

Never edit files to fix it — only find out why, for the comment:

- Compare against the base branch's latest run: `gh run list --branch
  <base> --limit 1 --json conclusion` — same failure there means it
  **predates** this PR, not caused by it.
- If it's not present on the base branch, skim the failing job's log tail
  (`gh run view <run-id> --log-failed`) for a one-line cause.
- A failure that disappears on a single rerun (`gh run rerun <run-id>
  --failed`) is transient/flaky — say so; don't rerun repeatedly chasing
  green.

### 6. Decide

All three gates must pass to merge. Any one failing holds the PR:

| Gate verdict | CI | Rebase | Verdict |
|---|---|---|---|
| AUTO (patch or minor) | green | clean (`CLEAN`/`BEHIND`) | **Approve + rebase-merge** (Template A) |
| AUTO | green | `DIRTY`/`UNKNOWN` after re-poll | **Comment**, hold (Template D) |
| HOLD — major | any | any | **Comment**, hold (Template B) — a major bump can break even with green CI |
| HOLD — downgrade | any | any | **Comment**, hold (Template B) — a version going backwards is never an expected Dependabot bump |
| HOLD — unchanged | any | any | **Comment**, hold (Template B) — nothing effective to approve |
| HOLD — conflict | any | any | **Comment**, hold (Template B) — the manifest diff and the PR body disagree about a version, so the real change is unclear |
| HOLD — unclassifiable | any | any | **Comment**, hold (Template B) |
| any | red or none | any | **Comment** with the Step 5 finding (Template C) |

Every severity `classify_bump.py` can emit has a row here; if you extend the
classifier, extend this table in the same change.

Templates: [references/review-templates.md](references/review-templates.md).

### 7. Show the plan, then confirm before writing anything

Before any `gh pr review` or `gh pr merge` call, print a table of every PR in
scope with its package(s), severity, gate verdict, CI status, rebase state,
and proposed action — stating explicitly which ones will be rebase-merged.
`gh pr review` and `gh pr merge` are both visible on GitHub, and a merge to
the default branch is not reversible by deleting a comment — get the user's
go-ahead on the plan before posting or merging any of them. Only skip this
pause if the invoking context already explicitly authorized an unattended
run.

### 8. Post the reviews, rebase-merge the eligible ones

```bash
gh pr review <number> --repo <repo> --approve --body "..."   # Template A
gh pr review <number> --repo <repo> --comment  --body "..."  # Template B/C/D
```

Never `--request-changes` — the point of Templates B/C/D is to flag for a
human decision, not block the PR.

For every PR approved under Template A, follow the approval with a rebase
merge:

```bash
gh pr merge <number> --repo <repo> --rebase --delete-branch
```

Rebase, not squash: these PRs are already one logical commit from a bot, and
a rebase keeps Dependabot's own commit (with its release-notes trailer and
signature) intact on the base branch. If the repo's settings disallow rebase
merging, `gh` will say so — report that and leave the approval standing
rather than silently switching strategy, since merge strategy is the repo
owner's decision.

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

If the base branch goes red after merging, report it immediately and
prominently, with the failing job and the merge commit, and name reverting
the merge as the available option. Do **not** push a fix to the base branch
to chase green: that converts a clean, revertible dependency merge into an
unreviewed direct commit on a protected branch.

### 10. Report

Summarize: how many approved and merged, how many approved but left unmerged
(and why), how many held (and which gate held them), how many needed CI
investigation (and the finding), and the post-merge base-branch status.
Link each PR.

## Notes

A Claude Code-specific variant of this skill, kept locally at
`~/.claude/skills/dependabot/` and not part of this portable copy, layers
`disable-model-invocation: true` (only fires on deliberate `/dependabot`,
never auto-invoked), `disallowed-tools: Edit Write NotebookEdit` (a
tool-level guardrail backing up the "never edit files" instruction above),
and named `repo`/`pr_number` arguments on top. Those fields aren't part of
the Agent Skills spec this repo's `skills-ref` validates, so they can't
travel with the portable copy — this copy relies on Step 7's confirmation
gate and the body's instructions for the same safety properties on every
host (Cursor, Codex, Claude).
