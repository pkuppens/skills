---
name: dependabot
description: Triage open Dependabot pull requests — identify which open PRs are actually bot-authored, classify each version bump as patch/minor/major from the diff (not just the title), verify CI is green, and post a formal GitHub review (not a plain comment) approving CI-verified patch/minor bumps. Use when the user wants to review, triage, clear out, or work through Dependabot PRs, dependency-update PRs, or version-bump PRs.
compatibility: Requires the gh CLI authenticated with read and pull-request-review access to the target repository.
allowed-tools: Bash(gh pr list*) Bash(gh pr view*) Bash(gh pr diff*) Bash(gh pr checks*) Bash(gh run list*) Bash(gh run view*) Bash(gh repo view*)
---

# Dependabot PR triage

Reviews open Dependabot PRs and posts a **formal GitHub review** for each —
`gh pr review`, which counts as a review contribution — never a bare `gh pr
comment`. This skill only ever identifies and comments: never edit source,
test, or config files to chase a green build — investigate and report the
finding instead (Step 4).

If invoked with a repo (`owner/name`) or a PR number, use it as the target.
Otherwise default to the current directory's repo (`gh repo view --json
nameWithOwner`) and every open Dependabot PR in it.

## Steps

### 1. Identify Dependabot PRs

```bash
gh pr list --repo <repo> --state open --json number,title,author,url,createdAt --limit 100
```

A PR is Dependabot-authored when `author.is_bot` is `true` **and**
`author.login` contains `dependabot` (observed as `app/dependabot`). If
`is_bot` is absent (some GitHub Enterprise setups omit it), fall back to the
title prefix `chore(deps` / `chore(deps-dev` / `build(deps`. If a specific PR
number was named, still confirm that PR is Dependabot-authored before
touching it — not every PR number a user names will be.

**Done when:** every open PR is sorted into "Dependabot" or "not" — the
non-Dependabot ones are excluded from every step below and never touched.

### 2. Classify each bump's severity

Run [scripts/classify_bump.py](scripts/classify_bump.py) (resolve the path
relative to this skill's own directory) against the PR's diff:

```bash
gh pr diff <number> --repo <repo> | python scripts/classify_bump.py
```

This parses every `"pkg": "old"` → `"pkg": "new"` pair in the diff and
compares versions as numeric tuples — never lexicographically, so `1.9.0` →
`1.11.0` reads as minor, not a downgrade. Group PRs ("Bump the npm-dev-deps
group with 7 updates") bump several packages at once; the script lists each
one and reports the **overall severity as the worst of them** — one major
package in a group makes the whole PR major.

If the script prints `NO_VERSION_CHANGES_FOUND` (non-npm ecosystem, or the
diff doesn't show the manifest), parse the PR title's "from X to Y" wording
by hand instead.

**Done when:** every Dependabot PR in scope has a severity — `patch`,
`minor`, `major`, or `unclassifiable` — with the specific old→new pair(s)
behind it, not just a guess from the title.

### 3. Check CI

```bash
gh pr checks <number> --repo <repo>
```

Classify as **green** (every check succeeded), **red** (any failed),
**pending**, or **none** (no workflow ran at all — distinct from green;
don't treat silence as success).

### 4. Investigate red or missing CI (skip if green)

Never edit files to fix it — only find out why, for the comment:

- Compare against the base branch's latest run: `gh run list --branch
  <base> --limit 1 --json conclusion` — same failure there means it
  **predates** this PR, not caused by it.
- If it's not present on the base branch, skim the failing job's log tail
  (`gh run view <run-id> --log-failed`) for a one-line cause.
- A failure that disappears on a single rerun (`gh run rerun <run-id>
  --failed`) is transient/flaky — say so; don't rerun repeatedly chasing
  green.

### 5. Decide

| Severity | CI | Verdict |
|---|---|---|
| patch or minor | green | **Approve** (Template A) |
| major | any | **Comment**, hold for human (Template B) — a major bump can be breaking even with green CI |
| unclassifiable | any | **Comment**, hold for human (Template B) |
| patch/minor/major | red or none | **Comment** with the investigation finding (Template C) |

Templates: [references/review-templates.md](references/review-templates.md).

### 6. Show the plan, then confirm before writing anything

Before any `gh pr review` call, print a table of every PR in scope with its
package(s), severity, CI status, and proposed verdict. `gh pr review` is
visible on GitHub and counts as a review contribution — get the user's
go-ahead on the plan before posting any of them, exactly as you would before
any other action that's visible to others. Only skip this pause if the
invoking context already explicitly authorized an unattended run.

### 7. Post the reviews

```bash
gh pr review <number> --repo <repo> --approve --body "..."   # Template A
gh pr review <number> --repo <repo> --comment  --body "..."  # Template B/C
```

Never `--request-changes` — the point of Template B/C is to flag for a
human decision, not block the PR.

**Done when:** every Dependabot PR in scope has either a posted review or an
explicit "skipped: `<reason>`" line in the final report — none silently
dropped.

### 8. Report

Summarize: how many approved, how many held for human judgement (and why),
how many needed CI investigation (and the finding), linking each PR.

## Notes

A Claude Code-specific variant of this skill, kept locally at
`~/.claude/skills/dependabot/` and not part of this portable copy, layers
`disable-model-invocation: true` (only fires on deliberate `/dependabot`,
never auto-invoked), `disallowed-tools: Edit Write NotebookEdit` (a
tool-level guardrail backing up the "never edit files" instruction above),
and named `repo`/`pr_number` arguments on top. Those fields aren't part of
the Agent Skills spec this repo's `skills-ref` validates, so they can't
travel with the portable copy — this copy relies on Step 6's confirmation
gate and the body's instructions for the same safety properties on every
host (Cursor, Codex, Claude).
