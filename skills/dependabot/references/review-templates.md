# Review comment templates

Disclosed reference for [`SKILL.md`](../SKILL.md). Fill the placeholders;
never post a template verbatim with unfilled `{...}` markers. Every template
names concrete packages, versions, and a CI run link — a bare "LGTM" is not
a formal review.

## A — Approve (patch/minor, CI green)

Used for `gh pr review <n> --approve --body "..."`.

```
CI/CD verified — {level} bump: {package list, e.g. "react-router 8.3.0 -> 8.3.1"}.
All checks passed: {ci_run_url}.
Approving as a routine, low-risk dependency update.
```

For a group PR with mixed levels, list every package with its own level and
state the overall as the worst one:

```
CI/CD verified — {overall_level} bump across {n} packages in this group:
- {pkg1}: {old1} -> {new1} ({level1})
- {pkg2}: {old2} -> {new2} ({level2})
All checks passed: {ci_run_url}.
Approving — overall severity is {overall_level}, CI is green.
```

## B — Comment, held for human judgement (major bump, or ambiguous)

Used for `gh pr review <n> --comment --body "..."` — never `--approve` and
never `--request-changes` for this case; the point is to flag, not block.

```
Holding this one for manual review: {package}: {old} -> {new} is a
{"major" | "unclassifiable"} bump.
CI status: {green | red | pending | no checks ran}.
Not auto-approving because {major version bumps can carry breaking changes
even with green CI | the diff didn't contain a clean version pair to classify}.
```

## C — Comment, CI investigation (red or missing CI)

Used for `gh pr review <n> --comment --body "..."`. Report the finding;
never edit source, test, or config files to chase a green run.

```
CI is currently {red | not running any workflow} on this PR.
Investigated: {failure also occurs on the latest {base_branch} run
({base_run_url}), so it predates this bump | failure does not occur on
{base_branch} — looks introduced by this bump | reran the failing job and
it passed the second time — looks transient/flaky | no workflow is
configured to run on this PR}.
Not making any code changes here — flagging for a decision on whether to
fix, rerun, or close.
```
