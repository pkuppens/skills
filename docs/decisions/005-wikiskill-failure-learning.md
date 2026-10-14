# ADR 005: WikiSkill-style failure learning — adopt partially

**Status:** Proposed
**Date:** 2026-10-13
**Context:** Issue [#37](https://github.com/pkuppens/skills/issues/37). Inputs: the paper [WikiSkill (arXiv 2608.27454)](https://arxiv.org/html/2608.27454v1), the `job_hunt` adoption in [ADR 003](https://github.com/pkuppens/job_hunt/blob/main/docs/adr/003-wikiskill-persistent-knowledge.md) ([job_hunt#71](https://github.com/pkuppens/job_hunt/issues/71)), and the session findings of [#43](https://github.com/pkuppens/skills/issues/43) in [docs/research/session-learning.md](../research/session-learning.md) ([PR #44](https://github.com/pkuppens/skills/pull/44)).

## Context

Skills in this library fail in use, and the reason is lost. The only rule today is
one bullet in [`_meta/skill-creation`](../../skills/_meta/skill-creation/SKILL.md):
"after errors or strong user feedback, update this meta-skill or the child skill".
Git keeps the edit, but nothing keeps *why* it was made, whether it helped, or the
attempts that were dropped.

**What the paper proposes.** WikiSkill splits agent experience into three layers:
raw execution traces, a wiki of root causes and strategies, and the skills the agent
reads. A Wiki Maintainer writes traces into the wiki. A Skill Proposer turns wiki
pages into one atomic skill edit. A gate accepts the edit only if the average score
on a validation split beats the best score so far; otherwise the skill rolls back.
The wiki is "never rolled back regardless of the acceptance decision" (§3.2.4). The
ablation backs the wiki: without it, average accuracy drops from 63.7% to 48.7%
(Table 3). The paper names its own limits: skills are injected directly, so
**triggering is not evaluated**; the strict gate drops neutral edits; and the wiki
has **no pruning**.

**What `job_hunt` decided** (ADR 003, accepted 2026-09-11). Keep the structure,
drop the automated loop: a per-session ritual run by a person (capture → maintain →
propose → gate → accept or revert), a per-domain gate (ruff + pytest for coding, a
1–5 rubric for the job hunt), a two-commit rollback, and six file formats under
`knowledge/{raw,wiki}/`. The implementation issues
([#75](https://github.com/pkuppens/job_hunt/issues/75),
[#76](https://github.com/pkuppens/job_hunt/issues/76),
[#90](https://github.com/pkuppens/job_hunt/issues/90)) are still open, so there is
no evidence yet of how the ritual works in practice.

**How this repo differs from both.**

| Aspect | Paper | `job_hunt` | This library |
| --- | --- | --- | --- |
| Where skills run | A rollout harness | The same repo | **Other repos.** Failures show up in consumer sessions, not here. |
| Failure scope | One environment | One repo | **Per consumer project.** The same skill can fail in one repo and work in another, because projects differ: pre-commit hooks or none, different CI checks, Dependabot configured or not. |
| Performance signal | Validation-split score | Tests, metrics, rubric | **None per skill.** CI checks structure only (ADR 001). |
| Usage volume | Full splits per iteration | Per session | **Thin.** One machine, ~6 weeks: 14 skills invoked, most once; `branch-cleanup` 21×, `dependabot` 11× (#43 R1). |
| Main failure kinds | Task errors | Task errors | Task errors **and triggering** (a skill fires when it should not, or never fires) — the part the paper does not evaluate. |
| Domains | One | Two (`coding`, `jobhunt`) | One: canonical skills. |

The hard part, as #37 predicted, is the gate. Two skills have a deterministic test
today: `dependabot` (`classify_bump.py --self-test`) and `branch-cleanup`
(`tests/test-cleanup.sh`). Neither runs in CI. Every other skill is prose, with no
signal beyond a human reading it. Usage evidence is per machine and incomplete; per
the [evidence rules](../research/session-learning.md), missing evidence proves nothing.

## Decision

**Adopt partially:** keep the wiki, atomic proposals, the proposal record, and the
"wiki survives a rollback" rule. Replace the numeric gate with a tiered gate. Scope
every pattern per consumer project: generic, conditional, or project-local (D6).
Defer any automated gate until a skill has a real signal.

### D1 — Three layers, mapped onto this repo

| Layer | Where | Committed? |
| --- | --- | --- |
| Raw | Local transcripts (`~/.claude/projects/` on each machine), PR review threads in consumer repos, the user's corrections. | **Never.** Raw transcripts can leak personal data, IP and errors ([CLAUDE.md](../../CLAUDE.md), `docs/research/`). Link a public PR thread; do not copy it. |
| Wiki | `docs/skill-wiki/`: one page per canonical skill, `patterns/<skill-name>.md`, plus `skill-impact.md` with one row per proposal. | Yes, distilled and anonymised. |
| Skill | `skills/<name>/` as today. | Yes. |

The wiki stays **outside `skills/`**. A consumer install copies skill folders, and
the agent that runs a skill must not load the wiki: the paper keeps the Inference
Agent away from it, and `job_hunt` D5 does the same. One page per skill, not one
per pattern, because volume is low; split a page when it passes about 150 lines.

### D2 — A manual proposer, one skill per proposal

A person, or an agent the person asks, runs the proposer when a canonical skill
fails in use or when a retro finds a pattern (#43 F5). Steps:

1. Add or update the pattern on the skill's wiki page: what happened, the root
   cause, the evidence (paraphrased, with machine, date, consumer repo and the
   project properties that matter), and the strategy.
2. Decide the pattern's scope (D6). If it is project-local, stop here: the lesson
   stays in the consumer repo.
3. Propose **one** change to **one** skill, which can be the `description`
   (triggering), a step, or a script. Add a `PENDING` row to `skill-impact.md`.
4. Run the gate (D3), then set the row to `ACCEPT` or `REVERT`.

This replaces the one-line "Self-improvement" bullet in `_meta/skill-creation`.

### D3 — A tiered gate instead of a validation score

| Tier | Applies to | Passes when |
| --- | --- | --- |
| G0 | Every proposal | The CI `validate` job is green (ADR 001). Structure only: it says nothing about the effect. |
| G1 | A change to a skill with a script | The skill's self-test passes, and a fix for a scripted failure first adds a test case that reproduces it. This is the bug-fix use of a [test oracle](../../CONTEXT.md): exactly one expected thing changes. A conditional change (D6) tests both cases: condition present and condition absent. |
| G2 | A prose-only change | The PR reviewer checks a short rubric: it cites a wiki pattern with at least one observed failure; it states the scope (D6) and, if conditional, names the condition and how the skill detects it; it changes one skill; it states the expected observable difference; projects without the condition see no change; the skill's other steps still read correctly; `SKILL.md` stays within ~300 lines. Merging the PR means `ACCEPT`. |

No tier claims that a skill *improved* — only that the change is justified and
broke nothing that can be checked. That is the honest limit with today's data.

### D4 — Rollback that fits squash merges

Put the wiki change and the skill change in **separate commits of one PR**. If the
gate fails before merge, drop the skill commit, set the row to `REVERT`, and merge
the wiki-only PR. If the problem shows up after merge, revert only the `skills/`
change in a new PR and add a `REVERT` row. The wiki is never rolled back.

### D5 — Scope boundary with #43

This ADR covers edits to **canonical skills**. #43 covers procedures, working
agreements, preferences and human habits (F1–F7); those are not skill edits a gate
can judge. A finding goes to the wiki when its target is a skill, and to #43's
follow-ups otherwise.

### D6 — Scope every pattern: generic, conditional, or project-local

A canonical skill runs in many consumer repos, and a failure in one repo can be a
non-issue in another. A skill about pre-commit hooks or CI checks, for example,
behaves differently in a repo that has neither. Before proposing a change, classify
the pattern:

| Scope | When | Where the lesson goes |
| --- | --- | --- |
| Generic | The root cause is in the skill itself, whatever the project. | A normal canonical skill edit (D2). |
| Conditional | The failure depends on a project property that can be detected, such as `.pre-commit-config.yaml`, `.github/workflows/`, `.github/dependabot.yml`, the OS and shell, or the toolchain. | A canonical skill edit that detects the property and branches on it. Projects without the property see no change. Detect it the way the [`terminal`](../../skills/terminal/SKILL.md) skill does: project docs, then probe files, then ask when they conflict. |
| Project-local | The failure depends on one repo's own conventions, not on a general property. | It stays in the consumer repo: its `CLAUDE.md`/`AGENTS.md`, or a **derivative skill** ([CONTEXT.md](../../CONTEXT.md)). It is not propagated here. |

Rules:

- **Start narrow.** With one observed project, choose the narrowest scope that
  explains the failure, usually conditional. Widen it to generic only when the root
  cause plainly sits in the skill text, or when a second project with different
  properties shows the same failure. A skill that worked elsewhere proves nothing
  either, per the evidence rules.
- **Lessons travel back as issues.** When a canonical skill fails in a consumer
  session, file an issue in this repo that names the skill, the symptom, and the
  project properties that matter, with a link to a public PR thread or a paraphrase
  of a private one. The proposer (D2) runs here. Consumers get the fix on their next
  **consumer install** update; a project-local fix never comes upstream.
- **Cap the branches.** When one skill collects more than about three conditions,
  split it into sub-skills, like the terminal skill tree, or into derivative skills,
  instead of adding a fourth branch.

## Alternatives considered

- **Adopt fully.** Needs a rollout harness and a per-skill score. Neither exists,
  and with most skills used once, a numeric gate would accept or reject on noise.
- **Decline.** Skill edits continue under the one-line rule with no record of why,
  and failed attempts leave nothing behind. The paper's ablation says this record is
  the part that matters most.
- **Copy the `job_hunt` layout as is.** Its domain split and six file formats serve
  an application with two domains and a test suite. This library has one domain and
  little volume; two files and one page per skill are enough to start.

## Consequences

**Good.** The *why* behind every skill edit survives, including dropped attempts.
Triggering failures get a place to land. The cost is small: one page per skill that
actually fails, and one table row per proposal.

**Bad.** G2 is human judgement, so a plausible but useless edit can pass. The wiki
can grow stale; like the paper, this ADR has no automated pruning. Evidence from one
machine stays partial. Conditional branches make a skill longer and harder to read;
the cap in D6 limits this, but does not remove it.

**Important.** G1 is the strongest tier, and it is cheap to extend: each scripted
failure leaves a regression test. Moving a fragile step from prose into a script
(the "low freedom" row in `_meta/skill-creation`) also moves it from G2 to G1.

## Follow-up issues

Drafted here for review; filed after the verdict is approved, then linked here.
Suggested order: W1 → W2 → W4; W3 can run at any time.

| ID | Title | Size | Scope |
| --- | --- | --- | --- |
| W1 | `[FEAT]: Scaffold docs/skill-wiki/ (page template + skill-impact.md)` | S | A README with the page template (evidence entries record the consumer repo and its relevant properties), the D2 steps, the D6 scope rules, and how to report a skill failure from another repo. An empty `skill-impact.md` table (`date`, `skill`, `pattern`, `scope`, `change`, `tier`, `result`, `PR`). |
| W2 | `[FEAT]: Replace the self-improvement bullet in _meta/skill-creation with the D2 proposer steps` | S | The steps and the D3 tiers, linking to `docs/skill-wiki/README.md` rather than copying it. |
| W3 | `[FEAT]: Run skill self-tests in CI` | S | Add `classify_bump.py --self-test` and `tests/test-cleanup.sh` to the `validate` workflow, so that G1 runs on every PR. Extends ADR 001; no conflict. |
| W4 | `[TASK]: Seed the wiki for branch-cleanup and dependabot, and run one proposal end to end` | S/M | Patterns from #43 R1 that #43 F1–F7 do not already own. `dependabot` is the first conditional example: it applies only where Dependabot is configured. Check D4 against a real squash-merged PR. |

## Revisit when

- A canonical skill reaches **at least 20 recorded uses in 30 days**, counted across
  both machines, with an outcome per use (accepted, corrected or reverted). Then
  consider a measured gate for that skill. Count a conditional branch only over the
  uses where its condition holds.
- An eval suite runs for a skill in CI (for example `claude plugin eval`, not
  evaluated here). Then it becomes that skill's G1.
- `skill-impact.md` shows **three or more prose-only edits reverted after merge**.
  Then the G2 rubric is not working and needs a stronger check.
- `job_hunt#76` ships its ritual. Then compare its practice with D2–D4 and align
  where it proves better.
