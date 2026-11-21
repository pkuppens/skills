# Classifier and CI investigation notes

Disclosed reference for [`SKILL.md`](../SKILL.md) Steps 2 and 5.

## Body reconciliation and warnings

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

## GitHub Actions tags

**GitHub Actions tags (`@v5` → `@v7`).** An Action's tag has one numeric
component and no minor/patch, so "major" says nothing about breakage risk
and CI exercising the new version is the real check. When the package is an
Action seen in a workflow file (`uses: owner/repo@vN` under
`.github/workflows/` or an `action.yml`) and *both* versions are
single-level, the classifier reports severity `tag` and the gate is `AUTO`
for an increase. A decrease or no-op still HOLDs, a mix of shapes
(`5` → `6.0.0`) falls back to semver, and single-level versions that are
*not* Actions (Docker `node:20` → `22`, calver `2024` → `2025`) are read as
semver majors and HOLD — PR CI does not exercise a runtime or schema change.
Before approving a `tag` bump, glance at the touched workflow's triggers:
if it only runs on release, tag, or deploy events, PR CI did not exercise
the new version, so hold it (Template B).

## Red or missing CI

Never edit files to fix it — only find out why, for the comment:

- Compare against the base branch's latest run: `gh run list --branch
  <base> --limit 1 --json conclusion` — same failure there means it
  **predates** this PR, not caused by it.
- A green base run is only evidence if it is recent enough to have seen the
  same inputs. Audit and scanning jobs depend on an advisory database that
  changes daily, so an old green run proves nothing about today. When the
  failing job is one of those, or the base run is older than a day, rerun
  that base workflow once (`gh run rerun <base-run-id>`) and compare against
  the fresh result. When the base branch has moved since that run, dispatch
  it on the current base SHA instead (R7 in
  [references/review-checks.md](references/review-checks.md)).
- If it's not present on the base branch, skim the failing job's log tail
  (`gh run view <run-id> --log-failed`) for a one-line cause.
- A failure that disappears on a single rerun (`gh run rerun <run-id>
  --failed`) is transient/flaky — say so; don't rerun repeatedly chasing
  green.
