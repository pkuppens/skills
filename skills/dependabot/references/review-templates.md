# Review comment templates

Disclosed reference for [`SKILL.md`](../SKILL.md). Fill the placeholders;
never post a template verbatim with unfilled `{...}` markers. Every template
names concrete packages, versions, and a CI run link. A bare "LGTM" is not a
formal review. Write in simple English, short sentences.

GitHub renders the body as markdown, so every comment uses the same skeleton.
The first line is a complete summary: the reader can stop there.

Which template to use is decided by the table in SKILL.md Step 6. A is the
only one that approves, and the only one followed by a merge. B, C and D post
`--comment` and leave the PR for a human. E is posted after the fact, on a PR
that was merged and then reverted (Step 9).

## The skeleton (all templates)

````markdown
**Verdict:** Approve and merge | Hold — {one-line reason}

### Explanation
{Two or three short sentences. Why this verdict. For a routine approval:
"Meets the conditions for a safe dependency update."}

### Packages
| Package | From | To | Level | Direct/indirect | Published | Cooldown |
|---|---|---|---|---|---|---|
| {pkg} | {old} | {new} | {major / minor / patch / tag} | {direct / indirect} | {date} | {met / matures {date} / exempt: advisory} |

### Evidence
| Check | Result |
|---|---|
| CI | {green / red / pending / none} — [run]({ci_run_url}) on `{head_sha}` |
| Rebase | {CLEAN / BEHIND / DIRTY / UNKNOWN} |
| R1 Branch integrity | {pass / note / hold}: {short} |
| R2 Change reconciliation | {pass / note / hold}: {short} |
| R3 Lockfile | {pass / note / hold}: {command} |
| R4 Usage | {pass / note / hold}: {short} |
| R5 Checks | {pass / note / hold}: {suite, n tests in CI} |
| R6 Local repetition | {pass / note / hold}: {commands} or not run: {reason} |
| R7 Base evidence | {base_branch} @ {base_sha}: [run]({base_run_url}) ({conclusion}) |

<details><summary>R1 and R2 details</summary>

{R1 patch-ID comparison. R2 file list and transitive list:
`{pkg} {old} -> {new}, required by {bumped pkg}`.}

</details>

### Recommendation
- {Concrete next step. When the step is "wait", give the date.}
````

Rules:

- The first line (`**Verdict:**`) is the summary. A verdict that needs two
  lines is too vague.
- Packages: one row per package, every package in a group. The overall level
  is the worst one: say it in the Explanation for a group.
- `Direct/indirect` comes from `classify_bump.py --manifest`. `unknown` counts as
  direct.
- Evidence: one row per check, `pass`, `note` or `hold` first. Long findings
  go under `<details>`, not in the table cell. Rows for checks that were not
  run say `not run: {reason}`. For C, D and E, drop the rows that do not apply
  (for example R1–R7 on a red-CI comment) and keep CI and Rebase.
- Merge line: Template A ends its Explanation with "Merging by {squash |
  rebase} as {you}; the Dependabot branch is deleted afterwards."
- Check how the comment looks in the GitHub preview before the first real
  post of a changed template (headings, both tables, the `<details>` block).

## A — Approve (gate AUTO, CI green, rebase clean)

Used for `gh pr review <n> --approve --body "..."`, then `gh pr merge <n>
<strategy from Step 0> --delete-branch`, with `--author-email <your noreply address>` for squash only.

````markdown
**Verdict:** Approve and merge

### Explanation
Meets the conditions for a safe dependency update: {level} bump of {package list, e.g. "react-router 8.3.0 -> 8.3.1"}.
CI is green, the rebase is {CLEAN | BEHIND}, and review checks R1–R6 {pass | pass with notes}.
Merging by {squash | rebase} as {you}; the Dependabot branch is deleted afterwards.

{Packages table} {Evidence table} {Recommendation: "None." or notes, with issue links}
````

**Patch or tag in cooldown.** Add this line to the Explanation and set the
`Cooldown` cell to `not met, notice`:

```
Notice: {package} {version} is {days} days old; the cooldown is {cooldown} days. A patch may pass; it matures on {date}.
```

**GitHub Actions tag** (`actions/checkout@v5` → `@v7`). Level is `tag`: no
semver applies, so green CI is the gate. Say so in the Explanation: "single-level
tag bump (no semver); CI ran the new version."

**Group PR with mixed levels.** One row per package in the table. The Explanation
names the overall level (the worst) and says no package changes its breaking
component.

### A, major variant — approve an authorized major

Only when the user's invocation explicitly authorized majors (SKILL.md Step 0).
Quote the authorization in the Explanation. Report the M1–M4 evidence from
[major-bumps.md](major-bumps.md), including any condition that is not met:

````markdown
**Verdict:** Approve and merge — major update, on the user's explicit authorization

### Explanation
Merging {package} {old} -> {new} (plus {n} minor/patch updates in this group) on the
authorization "{quoted words}". Any M1–M4 condition that is not met is listed below.

{Packages table, cooldown column filled for every package}

### Evidence
{Evidence table, plus these rows:}
| M2 Usage | {direct | indirect via {layer}}: {where}. Breaking changes: {each one, used / not used} |
| M3 Coverage | {suite} on `{head_sha}`: {passed}/{total} tests, locally with `{ci install command}` and in [CI]({ci_run_url}). {Added or manual: ...} {Indirect: {layer} admits {new major}, its tests passed} |
````

### A, indirect-major variant — approve an indirect major

Under the [indirect major rule](major-bumps.md#indirect-major-rule). No user
authorization is needed. Name the parents, because they are the reason it passes:

````markdown
**Verdict:** Approve and merge — indirect major, parents unchanged or minor/patch

### Explanation
{package} {old} -> {new} is a major bump, but nothing in the project calls it.
It is required by {parent list}; each parent is {unchanged | bumped by a minor or patch}
and its declared range `{range}` admits {new}. Cooldown is met and R1–R6 pass.

{Packages table} {Evidence table, R5 row names the parent's suite}
````

### Evidence in the tables

R-row wording for the Evidence table, with examples:

- R1: `pass` or `note: {author} commit {sha}, patch ID equals Dependabot commit`
- R2: `pass: {files}` or `note: transitive {pkg old -> new}, required by {bumped pkg}`
- R4: `pass: {consumers} via {dependency path}; imported in {modules | none: run by {config/task}}`
- R5: `pass: consumer suite ran in CI, {n} tests` or `note: not run in CI: {checks}`

### Line comments and threads (optional)

To anchor findings on the changed lock or manifest entries, post the review
through the API instead of `gh pr review`. Use `line` and `side: RIGHT`, on
lines inside the diff hunks:

```bash
gh api repos/<repo>/pulls/<n>/reviews --input review.json
# review.json: {"commit_id": "<head_sha>", "event": "APPROVE" | "COMMENT",
#               "body": "...", "comments": [{"path": "uv.lock", "line": 1055, "side": "RIGHT", "body": "..."}]}
```

Each line comment opens a review thread. A repository that requires resolved
conversations keeps the PR `BLOCKED` until every thread is resolved. Resolve
purely informational threads before `gh pr merge`. Leave a thread open when
it asks a human to act:

```bash
gh api graphql -f query='{repository(owner:"<o>",name:"<r>"){pullRequest(number:<n>){reviewThreads(first:50){nodes{id isResolved}}}}}'
gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"<id>"}){thread{isResolved}}}'
```

## B — Comment, held for human judgement

Used for `gh pr review <n> --comment --body "..."`. Never `--approve` and
never `--request-changes`: the point is to flag, not block. Use the skeleton.
Pick the verdict and Explanation that match why the gate held, so the comment
says something specific.

| Why | `Verdict:` line | Explanation |
|---|---|---|
| Major, not authorized (or R1/R2 holds) | `Hold — major bump, needs a human decision` | `{package}: {old} -> {new} is a major bump. A major can break even with green CI: someone needs to read the release notes. M1–M4 evidence is in the tables. Will qualify once {the missing evidence}.` |
| Major, cooldown not met | `Hold — {package} {new} matures on {date}` | `{package}@{new} was published {date}, {days} days ago; the cooldown is {cooldown} days. A major waits. Re-run the check on {date}.` |
| Minor, cooldown not met | `Hold for a human look — {package} {new} is {days} days old (cooldown {cooldown})` | `A young minor may bring new behavior. Read the release notes: {link}. Nothing else holds; approve after reading, or wait until {date}.` Do not merge. |
| Downgrade | `Hold — version decrease` | `{package}: {old} -> {new} is a decrease, not a bump. It usually means a yanked release, a pinned transitive constraint, or a misread manifest. Worth understanding before merging.` |
| Unchanged | `Hold — no effective version change` | `The diff does not move {package} off {old}. An empty bump usually means the real change is somewhere the version parser did not look.` |
| Conflict | `Hold — diff and PR body disagree` | `The manifest diff says {package} {diff_old} -> {diff_new}; the PR body says {body_old} -> {body_new}. Picking one would be a guess, and the severity differs depending on which is right.` |
| Unclassifiable | `Hold — severity unknown` | `Could not pin a concrete old -> new pair for {package \| this PR}. The severity is unknown, not low.` |
| Count mismatch | `Hold — package list incomplete` | `The PR body says {n_claimed} updates but only {n_resolved} matched a version pair ({package list}). An approval naming {n_resolved} of {n_claimed} would be incomplete.` |
| Review check held | `Hold — review check {R#} found a problem` | `{level} bump {package}: {old} -> {new} passes the version, CI and rebase gates, but {R#} holds: {finding, e.g. "the consumer's suite did not run in CI" \| "uv lock --check fails" \| "commit {sha} by {author} changes the effective diff"}. Not approving until a human decides on {R#}.` |

Set the `Level`, `Direct/indirect` and `Cooldown` cells for every row in the
Packages table, and mark the package that caused the hold. When more than one
hold applies (for example red CI *and* a count mismatch), post one review that
covers each reason, with the first reason in the `Verdict:` line, not one
review per reason.

## C — Comment, CI investigation (red or missing CI)

Used for `gh pr review <n> --comment --body "..."`. Report the finding;
never edit source, test, or config files to chase a green run.

````markdown
**Verdict:** Hold — CI is {red | not running any workflow} on this PR

### Explanation
Investigated: {failure also occurs on the latest {base_branch} run
([run]({base_run_url})), so it predates this bump | failure does not occur on
{base_branch}, so it looks introduced by this bump | the failing job passed on
a rerun, so it looks flaky | no workflow is configured to run on this PR}.
No code changes made here. A human decides: fix, rerun, or close.

{Packages table} {Evidence table: CI and Rebase rows}

### Recommendation
- {Next step, optional}
````

## D — Comment, rebase not clean

Used for `gh pr review <n> --comment --body "..."`. The version and CI gates
passed; only the rebase gate held, so this is usually a one-command fix for
the bot.

````markdown
**Verdict:** Hold — does not rebase cleanly (`mergeable={mergeable}`, `mergeStateStatus={mergeStateStatus}`)

### Explanation
The version and CI gates pass ({level} bump, checks green at {ci_run_url}).
{Conflicts against {base_branch}: asking Dependabot to rebase.
 | GitHub still reports mergeability as UNKNOWN after re-polling, so holding rather than guessing.
 | Blocked by branch protection: {which rule}.}
Not merging while the rebase is not a clean replay.

{Packages table} {Evidence table: CI and Rebase rows}

### Recommendation
- {Conflicts only: `@dependabot rebase`}
````

Put the literal `@dependabot rebase` in the Recommendation only when conflicts
are the actual cause. It is a command the bot acts on, so do not post it for an
`UNKNOWN` or `BLOCKED` state where a rebase would not help.

## E — Comment, merged then reverted (base branch went red)

Used for `gh pr review <n> --comment --body "..."` on the original, already
merged PR once the revert PR exists. It records the cause where the next
reader of this bump will look.

````markdown
**Verdict:** Reverted in #{revert_pr} — {base_branch} went red after this merged

### Explanation
Failing run: [run]({base_run_url}), {failing job}: {one-line cause}.
A rerun still failed, so it is not transient. The pre-merge baseline ([run]({baseline_run_url})) was green.
{Isolated to this merge by its own base run | Reverted together with #{other_prs}: the base runs could not separate them.}
Cause: {from the failing log, with the log line}.

{Packages table}

### Evidence
| Check | Result |
|---|---|
| Failing run | [{failing job}]({base_run_url}) |
| Baseline | [green]({baseline_run_url}) |

### Recommendation
- {From the cause table in revert-procedure.md, e.g. "fix-forward PR adapting {code}, then re-apply" | "ignore {version} in dependabot.yml until {condition}"}
- No fix attempted here. Dependabot will offer this update again; someone needs to look at {failing job} first.
````
