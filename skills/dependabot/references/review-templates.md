# Review comment templates

Disclosed reference for [`SKILL.md`](../SKILL.md). Fill the placeholders;
never post a template verbatim with unfilled `{...}` markers. Every template
names concrete packages, versions, and a CI run link — a bare "LGTM" is not
a formal review.

Which template to use is decided by the table in SKILL.md Step 6. The short
version: A is the only one that approves, and the only one followed by a
merge; B, C, and D all post `--comment` and leave the PR for a human.

## A — Approve (gate AUTO, CI green, rebase clean)

Used for `gh pr review <n> --approve --body "..."`, then `gh pr merge <n>
--rebase --delete-branch`.

```
CI/CD verified — {level} bump: {package list, e.g. "react-router 8.3.0 -> 8.3.1"}.
All checks passed: {ci_run_url}.
Rebase state: {CLEAN | BEHIND} — merges without conflicts.
Approving as a routine, low-risk dependency update; rebase-merging.
```

For a group PR with mixed levels, list every package with its own level and
state the overall as the worst one:

```
CI/CD verified — {overall_level} bump across {n} packages in this group:
- {pkg1}: {old1} -> {new1} ({level1})
- {pkg2}: {old2} -> {new2} ({level2})
All checks passed: {ci_run_url}.
Rebase state: {CLEAN | BEHIND} — merges without conflicts.
Approving — overall severity is {overall_level}, same major throughout, CI is green.
```

## B — Comment, held for human judgement (version gate held)

Used for `gh pr review <n> --comment --body "..."` — never `--approve` and
never `--request-changes` for this case; the point is to flag, not block.

Pick the sentence matching why the gate held, so the comment says something
specific rather than a generic "needs review".

**Major bump:**

```
Holding this one for manual review: {package}: {old} -> {new} is a major bump.
CI status: {green | red | pending | no checks ran}.
Not auto-approving because a major version bump can carry breaking changes
even with green CI — this needs someone to read the release notes.
```

**Downgrade (any component going backwards overall):**

```
Holding this one for manual review: {package}: {old} -> {new} is a version
*decrease*, not a bump.
CI status: {green | red | pending | no checks ran}.
Not auto-approving because a dependency going backwards is not an expected
Dependabot update — it usually means a yanked release, a pinned transitive
constraint, or a misread manifest. Worth understanding before merging.
```

**Unchanged — no effective version movement:**

```
Holding this one for manual review: the diff doesn't move {package} off
{old} — there's no effective version change to approve.
CI status: {green | red | pending | no checks ran}.
Flagging rather than approving, since an empty bump usually means the real
change is somewhere the version parser didn't look.
```

**Unclassifiable:**

```
Holding this one for manual review: couldn't pin down a concrete old -> new
version pair for {package | this PR}.
CI status: {green | red | pending | no checks ran}.
Not auto-approving because the diff didn't contain a clean version pair to
classify {and the title's wording was ambiguous}, so the severity is unknown
rather than low.
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

## D — Comment, rebase not clean

Used for `gh pr review <n> --comment --body "..."`. The version and CI gates
passed; only the rebase gate held, so this is usually a one-command fix for
the bot rather than a human judgement call.

```
Version and CI gates both pass ({level} bump: {package}: {old} -> {new},
checks green at {ci_run_url}), but this doesn't rebase cleanly right now —
mergeable={mergeable}, mergeStateStatus={mergeStateStatus}.
{Conflicts against {base_branch}: asking Dependabot to rebase — @dependabot rebase
 | GitHub still reports mergeability as UNKNOWN after re-polling, so holding
   rather than guessing
 | Blocked by branch protection: {which rule}}.
Not merging while the rebase isn't a clean replay — holding until it is.
```

Only include the literal `@dependabot rebase` line when conflicts are the
actual cause; it is a command the bot acts on, so don't post it speculatively
for an `UNKNOWN` or `BLOCKED` state where a rebase wouldn't help.
