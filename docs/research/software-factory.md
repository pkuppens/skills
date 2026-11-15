# Software factory: findings from the ZazenCodes video and reference repos

Issue: [#60](https://github.com/pkuppens/skills/issues/60), part of epic [#59](https://github.com/pkuppens/skills/issues/59). Date: 2026-11-13. Status: **distilled research, for review**.

This note is paraphrase plus short quotes. No transcript passage is reproduced; the raw transcript is not committed (see [session-learning.md](session-learning.md) for why).

## Sources

| Source | Link | Notes |
|---|---|---|
| Video | [Build Your Own AI Software Factory with Claude Code](https://www.youtube.com/watch?v=ctoaIC4LHmI) | ZazenCodes, 2026-10-07, 28:02. Chapters: 0:00 factories · 3:48 build · 10:20 run and approve · 16:16 parallel · 23:57 next steps |
| Build prompt | [`BUILD_PROMPT.md`](https://github.com/zazencodes/zazencodes-season-3/blob/main/src/software-factory-claude-code/BUILD_PROMPT.md) | The single prompt that generated v1 |
| v1 | [`software-factory-claude-code`](https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code) | One skill, seven agents, `board.json`, dashboard |
| v2 | [`software-factory-claude-code-v2`](https://github.com/zazencodes/zazencodes-season-3/tree/main/src/software-factory-claude-code-v2), read via [`DESIGN.md`](https://github.com/zazencodes/zazencodes-season-3/blob/main/src/software-factory-claude-code-v2/DESIGN.md) | The video's "next steps" built out |

Read against commit `94f7ae7` of the reference repo.

## The loop (v1, 4:35–6:52 and the build prompt)

`feature → spec-writer → builder → four parallel reviewers (security, ux, ui, code) → wait for all → any CHANGES: resume the same builder (max 2 rounds) → approver → APPROVE: merge, or ESCALATE: needs-human`.

- **Roles.** Spec writer, builder, four reviewers, approver. The orchestrator is the user's own Claude Code session running one `/factory` skill; it spawns every agent and is the only writer of state.
- **File contracts.** Agents get context from files, never from the conversation, and each writes exactly one file (`spec.md`, `build.md`, `round-N/review-<role>.md`, `decision.md`). The verdict is the first line (`VERDICT: PASS|CHANGES`, `APPROVE|ESCALATE`), so the orchestrator can read it without parsing prose.
- **State.** One folder per job, plus `board.json` and a `backlog.md` queue. The video gitignores it (15:18): it is transient, and committed it would clutter file search.
- **Commands.** `/factory <feature>`, `next`, `approve <id>`, `rework <id> <note>`.
- **Models.** Strong model as orchestrator; Opus for spec, build, security, approver; Sonnet for the other reviewers (19:08).
- **Resume, not respawn.** The builder is spawned by name and resumed with `SendMessage` each round, so it keeps its context.
- **Own it.** The video's point (19:54): the factory is small enough to read in one sitting, and the value is understanding the concepts, not installing a popular skill.

## What v2 changes (from its `DESIGN.md`)

| v1 | v2 |
|---|---|
| Feature typed into the session | GitHub issues labelled `factory` are the queue; intake agent returns ACCEPT / NEEDS-INFO / REJECT as an issue comment |
| Every verdict is an LLM opinion | `checks.sh` gate runs before any reviewer and again before merge; a failing build goes straight back to the builder |
| All four reviewers every time | Intake rates risk and surfaces; a script routes reviewers and models from `config.json` |
| Local `git merge`, needs a clean main checkout | A PR per issue ("Closes #n"), merged with `gh pr merge` |
| `/factory approve` | Merging the PR is the approval; ESCALATE leaves the PR ready with a label |
| `board.json` written by the orchestrator | `factory/bin/job` is the only writer of `job.json` and refuses illegal stage moves |
| Cost invisible | Cost per job, summed from subagent transcripts (fragile: not a documented format) |
| Branch can edit its own checks | Gate runs main's `checks.sh` and fails a branch that touches `protected_paths` |

Other v2 guardrails worth knowing: issue text reaches agents as quoted data, never as prompt; intake has no shell; agents push only `factory/*` branches; the factory never deploys.

## Parallel-mode lessons (16:16–23:57)

1. **Parallel jobs need isolation.** Without worktrees they collide; one worktree per job fixed it (16:04–19:08).
2. **Dirty main blocks merge.** The orchestrator's own `backlog.md` edits left main dirty, so the local merge refused (22:13). Factory bookkeeping must never count as dirt. v2's fix is to avoid the problem: state is gitignored and merging happens through a PR.
3. **Stale main blocks the second merge.** After the first job merged, the next one would not merge (23:46). Sync with main and re-gate before every merge (v2 does this).
4. **Over-escalation.** The approver sent nearly everything to a human, including a job where its own note said nothing was left for a human (21:27). Escalation criteria must be explicit and testable, for example a list of named reasons, not a general sense of caution.
5. **Cost.** Subagents pass context back and forth, so cost rises; the author ran on a flat plan (26:03–26:51) and measured nothing. v2 added per-job cost.
6. **Orchestrator model.** A Sonnet orchestrator at low effort started fast, but the author judged that subagents, not the orchestrator, set the pace and kept a strong orchestrator (18:23–19:08).

## Keep / change / drop

Target files are `TBD` until #61–#64 land; update this table as they do.

| Video idea | Verdict | Our design | Carried by |
|---|---|---|---|
| Files, not conversation, as the contract; one file per agent | Keep | Same | TBD (#61) |
| Verdict as first line of the file | Keep | Same | TBD (#61) |
| WAIT FOR ALL reviewers, then resume the same builder | Keep | Same | TBD (#61) |
| Round cap (2) | Keep | Configurable, default 2 | TBD (#61) |
| Gitignored, human-readable job state | Keep | Job files are plain markdown; no dashboard | TBD (#61) |
| Strong orchestrator, cheaper reviewers | Keep | Risk-based routing, as in v2 | TBD (#61) |
| Always worktree-per-job | Change | Linear by default (tweak 1): normal `feature/NNN-…` branch, worktrees only when `concurrency > 1` | TBD (#64) |
| Queue is `backlog.md` / typed feature | Change | GitHub issues with label `ready-for-agent`; intake bounces weak issues (tweak 2) | TBD (#63) |
| Verdicts from LLM reviewers alone | Change | Deterministic gate first: pre-commit, tests, coverage, lint (tweak 3) | TBD (#62) |
| Builder writes code, tests alongside | Change | Acceptance criteria become tests first (tweak 4) | TBD (#62) |
| Local merge on `/factory approve` | Change | Land through `finish-work`: PR, blocking CI watch, merge on formal APPROVE and green CI at the same head SHA (tweak 5) | TBD (#63) |
| Approver agent decides to merge | Change | Approver emits a verdict only; cannot self-approve while [#45](https://github.com/pkuppens/skills/issues/45) is open | TBD (#63) |
| Stop at merge | Change | Watch base branch after merge, revert through a PR if red (tweak 6) | TBD (#63) |
| Own bespoke merge, review, cleanup logic | Change | Compose `finish-work`, `dependabot`, `branch-cleanup`, `code-review`, `tdd`; the skill owns orchestration only (tweak 7) | TBD (#61) |
| Dashboard | Drop | Out of scope; revisit after first real run | n/a |
| Sentry / metrics intake | Drop | Out of scope for the epic | n/a |
| Copying v1/v2 files | Drop | Derive the design, write our own files | n/a |
| `checks.sh` single repo-specific script, protected paths | Change | Adopt the idea (gate cannot be edited by the branch it judges), using the repo's own pre-commit and CI commands | TBD (#62) |
| Per-job cost from transcripts | Change | Record turns and tokens per job; transcript parsing is undocumented, so treat as best-effort | TBD (#61) |

## Licensing position

- The GitHub API **now reports `gpl-3.0`** for the parent repo `zazencodes/zazencodes-season-3` (checked 2026-11-13). Epic #59 said it reported none; that is out of date.
- The v2 folder ships a full GPLv3 `LICENSE`, and its README offers a commercial license for closed-source use. v2's "what changed" table records v1 as previously unlicensed; v1's licence terms are therefore only those of the parent repo.
- **Position: do not copy text or code from v1 or v2.** GPLv3 is a strong copyleft licence; text copied into our skill could oblige us to release the derived work under GPLv3. Ideas, architecture and the stage vocabulary are not copyrightable, so this note and the new skill derive the design and write their own files. Quote at most short phrases, with attribution.
- If copying is ever wanted, ask the author for the commercial license they offer, or relicense our skill under GPLv3 knowingly.
- No claim here is legal advice; it is a working rule for this repo.
