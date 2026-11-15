# Review checks (Step 5a)

Disclosed reference for [`SKILL.md`](../SKILL.md). The three gates show that
the version step is safe and that CI passed. They do not show what CI tested,
whether the tested code uses the package, or whether the branch still holds
only Dependabot's change. These checks close that gap.

Run R1–R6 only on PRs that are still eligible for approval: gate AUTO, CI
green, and a clean rebase. A held PR gets R1 and R2 at most. R7 is about the
base branch, not the PR, so it runs once per invocation, as part of Step 7.

Contents: [R1](#r1--branch-integrity) · [R2](#r2--change-reconciliation) ·
[R3](#r3--lockfile-consistency) · [R4](#r4--usage) ·
[R5](#r5--check-the-checks) · [R6](#r6--local-repetition) ·
[R7](#r7--base-branch-evidence) · [Safety](#safety)

| # | Check | Holds the PR when | Note only when |
|---|---|---|---|
| R1 | Branch integrity | another author's commit changes the effective diff | another author's commit leaves the effective diff unchanged |
| R2 | Change reconciliation | a package changes that is neither in the body nor a dependency of a bumped package | hash-only changes (for example new wheels) |
| R3 | Lockfile consistency | the lock check fails | — |
| R4 | Usage | — | nothing uses the package; a declared lower bound cannot install on the project runtime |
| R5 | Check the checks | CI ran on another SHA, or a consumer's suite did not run | checks configured for a consumer that CI does not run |
| R6 | Local repetition | a consumer test or a check from the R5 gap list fails on the PR but passes on the base | it was not run (no local clone or no sandbox); results differ from CI but both pass |
| R7 | Base-branch evidence | no successful run exists for the current base SHA (blocks all merges, see Step 7) | — |

Record every result in the evidence block ([review-templates.md](review-templates.md)).

## Safety

R3 installs and R6 runs the code of the dependency under review. Never do this
in the user's own checkout. A throwaway worktree protects your files, not your
credentials:

```bash
git fetch origin pull/<n>/head
git worktree add /tmp/dependabot-<n> FETCH_HEAD     # throwaway, removed afterwards
git worktree remove --force /tmp/dependabot-<n>
```

Unsetting `GH_TOKEN` and `GITHUB_TOKEN` (`env -u GH_TOKEN -u GITHUB_TOKEN
<command>`) removes only those two variables. The `gh` keyring login, the git
credential helper and SSH keys stay reachable to code you run. So:

- **Preferred for R6:** run it in a container or VM that has none of those
  credentials mounted.
- **Without one:** run R6 only when the PR is a patch or minor bump of a
  package the repository already trusts. For anything else record R6 as "not
  run (no sandbox)", a note, and let CI carry the result.
- `--ignore-scripts` in R3 stops install scripts only. R6 executes the package
  anyway through the test run, so R3's flag is not a substitute for the above.

Use the installer options that skip install scripts (see R3). The rule
"never edit files" means never edit tracked files in the target repository.
A throwaway worktree, `.venv/` and `node_modules/` are fine.

## R1 — Branch integrity

```bash
git fetch origin <base>
git log --format='%h %an %s' origin/<base>..FETCH_HEAD
```

All commits should be from `dependabot[bot]`. Usually a human has merged the
base branch into the PR. To check whether the effective change is still
Dependabot's commit, compare patch IDs:

```bash
git diff <dependabot-sha>^ <dependabot-sha> | git patch-id --stable
git diff origin/<base>...<head-sha> | git patch-id --stable
```

When they are equal, R1 is a note. A rebase merge replays only the non-merge
commits. Dependabot refuses `@dependabot rebase` on a branch that someone
else has edited. Mention `@dependabot recreate` instead, which discards
those edits. Do not post it yourself: it changes the head SHA that you
reviewed.

## R2 — Change reconciliation

`gh pr diff <n> --repo <repo> --name-only` must list only the ecosystem's
manifest and lock files. In each lock hunk, every package with a version
change is either in the PR body or is a dependency of a bumped package. Use
the dependency graph to show this, not the release notes. Release notes
rarely name transitive pins:

| Ecosystem | Is X pulled in by bumped package P? |
|---|---|
| uv | `uv tree --invert --package <X>` |
| poetry | `poetry show --why <X>` |
| pip-tools | `pipdeptree -r -p <X>` |
| npm / pnpm / yarn | `npm explain <X>` / `pnpm why <X>` / `yarn why <X>` |

## R3 — Lockfile consistency

| Ecosystem | Command (no install scripts) |
|---|---|
| uv | `uv lock --check` (resolves only, installs nothing) |
| poetry | `poetry check --lock` |
| pip-tools | `pip-compile <options> --output-file=/tmp/req.txt <in-file>`, then `diff /tmp/req.txt <file>` |
| npm | `npm ci --ignore-scripts` |
| pnpm | `pnpm install --frozen-lockfile --ignore-scripts` |
| yarn | Yarn 1: `yarn install --frozen-lockfile --ignore-scripts`; Yarn 2+: `yarn install --immutable --mode=skip-build` |
| GitHub Actions | not applicable |

## R4 — Usage

Find the consumers: the workspace members or packages that depend on the
bumped package, and the modules that import it. Use the R2 commands for the
dependency path. To find the importers, search project-owned code for
`import <module>` / `from <module>` or `from '<pkg>'` / `require('<pkg>')`.
Exclude vendored, generated and analysed trees. For an Action, search for
`uses: <owner>/<repo>@` under `.github/`. A tool without importers (linters,
type stubs, build tools) is normal. Name the config or task that runs it.

## R5 — Check the checks

```bash
gh pr view <n> --repo <repo> --json headRefOid,statusCheckRollup
gh run view <run-id> --repo <repo> --json headSha
gh run view <run-id> --repo <repo> --log | grep -E '<consumer suite>|passed|failed'
```

Confirm three things. First, the run's `headSha` equals the PR head. Second,
the log shows each consumer's suite from R4, with a test count. Third, list
the checks that the consumer configures but CI does not run (type checker,
linters, an integration suite). R6 covers those checks.

## R6 — Local repetition

In the throwaway worktree (see [Safety](#safety)), run the tests of the code
that uses the package, plus the checks from the R5 gap list. The consumers
come from R4. Use the repository's task runner where one exists, and record
the commands and the test counts.

Select the tests by the importers found in R4:

| Ecosystem | Run only the tests that exercise the consumers |
|---|---|
| npm / pnpm / yarn | test files that import the package: `npm test -- <files>` (vitest and jest also accept `--related <source-files>`) |
| uv / poetry / pip-tools | `uv run pytest <paths>` / `poetry run pytest <paths>` for the test files that import the package or the modules from R4 |
| GitHub Actions | no tests; confirm the workflow that uses the Action ran green on the head SHA (R5) |

Selection rules:

- A test file counts as a consumer when it imports the package, or imports a
  module from R4 that does. Follow one level of project-owned imports; stop
  there.
- When no test file qualifies (a tool, a type stub, a build dependency), or
  the whole suite finishes in a few minutes, run the whole suite instead.
  A too-narrow selection is worse than a slow run.
- A major-version difference in the package's own behaviour (for example a
  DOM implementation or a test environment) is a reason to run the whole
  suite, because the effect reaches every test.
- Repeat the run once on the base branch when a test fails, to show whether the
  bump caused the failure. Hold only when the base passes and the PR fails.

The full suite on the head SHA belongs in CI. R6 adds the selected tests, run
locally, for the consumers and checks that CI did not run.

## R7 — Base-branch evidence

```bash
git ls-remote origin refs/heads/<base>
gh run list --repo <repo> --branch <base> --workflow <ci-workflow> --limit 1 \
  --json databaseId,headSha,conclusion,url
```

The latest completed run must be for the current base SHA. If it is for an
older commit and the workflow supports `workflow_dispatch`, start it, look up
the run it created, and watch it:

```bash
gh workflow run <ci-workflow> --repo <repo> --ref <base>
gh run list --repo <repo> --workflow <ci-workflow> --branch <base> \
  --event workflow_dispatch --limit 1 --json databaseId,headSha
gh run watch <run-id> --repo <repo> --exit-status
```

If the workflow cannot be dispatched, record the gap and treat the base
branch as not proven green: post reviews, but merge nothing.
