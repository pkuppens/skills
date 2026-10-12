# Session learning: findings (first pass)

Issue: [#43](https://github.com/pkuppens/skills/issues/43). Date: 2026-10-11, revised 2026-10-12 after review. Status: **first pass, for review**. Verdicts are provisional: they hold until new evidence contradicts them.

This document contains no raw transcript text. Quotes from prompts are short paraphrases. Personal, non-code sessions appear only as counts.

## Evidence rules

- **Local evidence can add or change a learning. Missing evidence proves nothing.** The user works on two machines (a PC and a notebook), cleans up sessions, and may work with coworkers. A pattern that does not show up here may still be real. Evidence from this machine can support a "pursue" verdict, but its absence never justifies "close".
- Every learning traces to a concrete moment: a session, a PR, or a commit.
- The data is a snapshot that shrinks over time. Between the first run (2026-10-11) and the second (2026-10-12), one session file was cleaned up (58 → 57). Counts below are from the first run unless marked otherwise.

## Summary

- **The most important finding: finishing work is one repeated procedure.** About 15 prompts across 6 repos ask for the same "I think I'm done, now finish it" sequence: an in-depth AI review, tool and CI checks, a simple AI judgement for trivial items, a formal review, rebase-merge, branch cleanup, and watching main. The two most-used skills (`branch-cleanup`: 21 uses, `dependabot`: 11) are parts of it. Not every step applies to every repo: `dependabot` applies only where Dependabot is configured. → F4.
- **Keyword detection of corrections does not work for this user.** It finds 3 corrections in 112 prompts (with "instead" counted); reading by hand finds about 8. The user phrases corrections positively and folds them into the next instruction ("do this on the branch you left open"). Some questions are real questions, and some are polite requests for a correction. Classification needs an LLM, and it can be helped by optional intent prefixes (`Question:`, `Correction:`, `Task:`). The user already used `question:` once. → F7.
- **User-level preferences are stuck in project memory.** Five preferences that apply everywhere are each saved in only one project's memory. Example: "draft issues in `tmp/` before filing" lives in `context-smith` memory, so this session filed #43 directly, against that preference. → F2.
- **WikiSkill overlaps with this approach, but the two are not the same.** WikiSkill improves *task skills* through a gated proposer loop. This approach also targets procedures, human habits and cross-project preferences. See [WikiSkill compared with this approach](#wikiskill-compared-with-this-approach). A WikiSkill loop already runs in `job_hunt` ([ADR 003](https://github.com/pkuppens/job_hunt/blob/main/docs/adr/003-wikiskill-persistent-knowledge.md), [job_hunt#71](https://github.com/pkuppens/job_hunt/issues/71)).
- Tool errors are rare (121 of 3,213 calls, 3.8%) and mostly harmless exploration, such as probing for files that do not exist. They are not the main source of rework.

## Prerequisites and related work

#43 has **no blocking prerequisites**. Related work:

| Item | Relation |
|---|---|
| [#37](https://github.com/pkuppens/skills/issues/37) WikiSkill spike | Consumes R1, idea 5 and the WikiSkill comparison here. |
| [job_hunt#70](https://github.com/pkuppens/job_hunt/issues/70) WikiSkill epic | Sibling implementation. #71 ADR and #72 scaffold are closed; #75 (raw trace capture), #76 (ritual and gate) and #90 (Langfuse trace → raw) are open. |
| [job_hunt#82](https://github.com/pkuppens/job_hunt/issues/82) | Decided on ADR length-budget checks: the "context economy" theme in R2. |

## R1: Session archaeology

Method: [scripts/mine_sessions.py](scripts/mine_sessions.py) parses `~/.claude/projects/**/*.jsonl` on one machine and prints counts only. Raw snippets go to the gitignored `tmp/` when `--examples` is passed. After that, the 112 prompts were read by hand.

### Counts (one machine)

| Signal | Count |
|---|---|
| Sessions (incl. 8 subagent files) | 58 (57 on the second run) |
| Human prompts | 112 |
| Tool calls | 3,213 |
| Tool errors | 121 (3.8%; 99 of them Bash) |
| User interrupts | 3 |
| Keyword-detected corrections | 3 (manual reading: about 8) |
| Prompts with an intent prefix | 1 (`question:`) |
| Files edited 5+ times in one session | 14 |
| Date range | 2026-06-17 to 2026-10-11; over 95% of records are from Sep–Oct |

Tool errors by class: nonzero exit (43), test/lint failure (31), file not found (20), permission denied (10), input validation (4), blocked by the harness (4), other (9).

### Failure classes worth acting on

| Class | Evidence | Kind |
|---|---|---|
| **Approving your own PR** | The user asks for a formal approval on PRs that their own account opened (the agent uses the user's `gh` login). GitHub rejects this (`Can not approve your own pull request`), and the auto-mode classifier blocked it twice as "Self-Approval". This is a GitHub-wide rule, not a repo setting: [pull request authors cannot approve their own pull requests](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews). Repo settings decide only whether an approval is *required* to merge. | Mechanical: detect, then choose (F1) |
| **Wrong branch or folder** | 3 prompts in 2 repos had to restate the branch ("from the correct branch", "on the branch you left open"). In one more case two sessions worked in the same folder. | Mechanical: a preflight check |
| **Retries instead of a root cause** | The agent retried an API error. The user said retries would not help and asked for a small prototype first. The fix was a request bug. | Judgement: `diagnosing-bugs` |
| **Sleep-polling CI** | 2 sleep-and-check chains blocked by the harness ("use Monitor"). | Mechanical: skill text |
| **Windows shell quirks** | Python Store alias, heredoc quote errors, "command line too long", JSON-escaping of `C:\` paths in tool input (2). | Mechanical: `terminal` skill |
| **"Could lint have caught this?"** | The user asked this after an undefined-function bug. | Mechanical: per-repo lint rule |

### Manually found corrections (paraphrased)

Restate the branch (×3) · don't fix with retries · write a prototype first · the PR still has leftovers, commit and push · is this setup option verified? · could a lint step have caught this earlier? · a factual correction to a claim the agent made about the user.

### Intent prefixes (proposal)

The same words can be a question or a task. With "Question: can you add authentication?" the user wants an answer, for example "no: requests are anonymous, and this needs a new layer with accounts and logins". With "Task: can you add authentication?" the user wants the work done. Proposal (F7):

- The user may start a prompt with `Question:`, `Correction:`, `Task:` or `Feedback:`. It is optional, never required.
- When the intent of a prompt is unclear *and* the difference matters, the agent asks once which one was meant, and may suggest the prefix for next time.
- Prefixed prompts give the retro labelled examples to check its classifier against. `mine_sessions.py` counts them already.

## R2: PR and commit archaeology

Source: the user's review comments on the last 40 merged PRs in 6 repos (196 comments). Most of the 123 long comments were written by an agent on the user's behalf, so this section counts only the comments the user wrote.

Repeated themes in the user's own comments:

1. **Show that it works.** "Does this have usage instructions or documented evidence it works?", "would like to see it in action", "would have liked an integration test", "needs full CI run", "didn't do a test run". This is the most frequent theme.
2. **Context economy.** "Bit verbose for an agent's context window?", "separate referenced document?" (×2), "a 380-line ADR is too long". Agent instructions leaked into user-facing text and had to be cut; scratch analysis had to move into a notebook in the repo.
3. **Precise terms.** Define ambiguous terms at first use and link them to `CONTEXT.md`. Keep established words ("Install", not "Attempt to install").
4. **Security.** Credentials leak when only some of them are provided.
5. **Dependency bumps.** About 25 near-identical "CI/CD approved minor bump" reviews. The `dependabot` skill now automates these: evidence that automating a repeated procedure pays off.

Mechanical checks already exist for whitespace and lint (pre-commit). Themes 1–3 are judgement calls, so they belong in skill text and PR templates, not in new linters.

## R3: aihero `/retro`, opinion by opinion

| `/retro` opinion | Verdict | Why |
|---|---|---|
| Fixes go into the environment, not the code | Adopt | Matches R1: the fixes are rules, checks and skills. |
| Mechanical → check, judgement → prose | Adopt | Already a principle in #43. |
| Every candidate traces to a session moment | Adopt | Prevents generic advice. |
| Standards belong to the reviewer, not the implementer | Adapt | Here the same agent often implements and reviews in one session. Put standards in skill references that both roles read. |
| `CLAUDE.md` holds pointers only | Adapt | Fits the user's "lean CLAUDE.md" memory. The workspace root `CLAUDE.md` holds process on purpose; move detail into linked docs. |
| It is not a memory system | Reject | In R6, memory holds most user-level learning. A retro must be allowed to write to memory or a decisions register. |
| User-invoked only | Adapt | Manual first. Schedule it only after it has proved useful (idea 9). |
| Single session | Reject as default | Recurrence across sessions is the best filter against noise. |
| Keyword-free, judgement-based detection | Adopt (implicit) | R1 shows keyword detection fails for this user. |

## R4: Existing session-reflection tools

Checked 2026-10-11 with `gh api`. Not yet installed or run.

| Tool | Stars | Last push | License | What it does | Verdict |
|---|---|---|---|---|---|
| [BayramAnnakov/claude-reflect](https://github.com/BayramAnnakov/claude-reflect) | 1,771 | 2026-10-03 | MIT | Captures corrections and feedback, updates CLAUDE.md with review; `--scan-history` for past sessions | **Trial first** (F3) |
| [millionco/claude-doctor](https://github.com/millionco/claude-doctor) | 622 | 2026-04-15 | none | Scores transcripts for anti-patterns (edit thrash, error loops), emits rules | Read-only reference; no license, so no derivative |
| [rlancemartin/claude-diary](https://github.com/rlancemartin/claude-diary) | 382 | 2025-12-17 | MIT | `/diary` and a pre-compact hook write session notes | Park; inactive, memory-only |
| harperreed `session-reflection-analysis` (in [dotfiles](https://github.com/harperreed/dotfiles)) | 334 | 2026-10-03 | none | Skill: reviews history, suggests CLAUDE.md, skill or command changes | Reference for prompt design |
| ed3d `review-session` (in [ed3d-plugins](https://github.com/ed3dai/ed3d-plugins)) | 250 | 2026-09-06 | none | Session review within a research-plan-implement workflow | Reference |
| caioniehues/claude-reflect | 0 | 2026-07-01 | MIT | Fork of BayramAnnakov/claude-reflect | Ignore; use upstream |

Build-vs-buy: trial `claude-reflect` against the R1 manual findings before writing our own retro skill. If it finds the implicit corrections, install it as a vendor skill and add only what is missing.

## R5: Literature (scan, not a full read)

| Work | Idea to reuse here |
|---|---|
| ACE, [arXiv 2510.04618](https://arxiv.org/abs/2510.04618) | Change a playbook by small, itemised edits, never full rewrites. Rewrites cause "context collapse": detail is lost. Apply this to skill edits. |
| WikiSkill ([arXiv 2608.27454](https://arxiv.org/html/2608.27454), #37) | See the comparison below. |
| Voyager (skill library) | A skill joins the library only after it has worked in execution. This matches R2 theme 1, "show that it works". |
| Reflexion | Verbal self-reflection stored per episode; useful inside a session, weak across sessions. |
| Dynamic Cheatsheet | Memory that adapts at test time; ACE builds on it. |

## WikiSkill compared with this approach

Sources: the paper summary in #37, and how `job_hunt` adapted it in [ADR 003](https://github.com/pkuppens/job_hunt/blob/main/docs/adr/003-wikiskill-persistent-knowledge.md): a human-run, per-session ritual with a per-domain gate and a two-commit rollback, instead of the paper's automated loop with a numeric reward.

| Aspect | WikiSkill (paper) | WikiSkill in `job_hunt` | This approach (#43) |
|---|---|---|---|
| What improves | Task skills | Task skills in two domains (coding, job hunt) | Task skills, **procedures** (finish-work), **checks**, **cross-project preferences**, and **the user's own habits** |
| Input | Execution traces from a rollout harness | Persona-free trace summary per session | Transcripts, PR reviews, commits, memory files, from several repos |
| Unit of learning | Wiki pattern → one atomic skill edit | Same; one skill per proposal | Finding → verdict → small issue; the target can be a skill, a check, memory, or a human habit |
| Who proposes | Skill Proposer agent | An agent, invoked by a person | A retro run (F5), then the human decides |
| Gate | Numeric performance gain; rollback otherwise | Coding: ruff + pytest (+ metrics later). Job hunt: 1–5 rubric | Human review of verdicts. There is no per-skill signal yet (idea 5) |
| What persists after a failed edit | The wiki | The wiki, plus a `REVERT` row in `skill-impact.md` | The findings doc and closed issues with a rationale |
| Scope | One agent, one task domain | One repo | Every repo, and the human–agent working agreement |
| Human side | None | Person runs the ritual | Mutual learning: what the human does that causes rework (digest, intent prefixes) |
| Evidence stance | Rewards from a benchmark | Gate output per proposal | Local evidence can add a learning; absence proves nothing |

**Overlap.** Both keep a durable record of *why*, separate from the instructions an agent reads, and both make small edits instead of rewrites. The R1 transcripts play the part of WikiSkill's raw layer. This findings doc is an early, single-file version of its wiki. A retro (F5) would play the part of the proposer.

**Differences that matter.** WikiSkill needs a measurable gate per skill, and this repo does not have one yet. WikiSkill only learns task skills, while R1 shows that the largest gains here are in *procedures and working agreements* (finish-work, own-PR reviews, preferences that apply everywhere). Those are not skill edits that a benchmark can gate.

**Implication.** The two are complementary. Take from WikiSkill: a wiki that survives a rollback, one atomic change per proposal, and recording every proposal before it lands. Keep from this approach: several target types, a human gate, and the human side of the loop. #37 should decide whether this repo uses the `job_hunt` layout for skill edits; the procedure and preference work (F1, F2, F4, F7) does not depend on that decision.

## R6: Memory audit

13 project memory folders, 27 files, on this machine. Findings:

- **User-level facts saved in one project only**: minimal responses and lean docs (`on_prem_rag`); formal PR reviews count toward the contribution streak (`production-agentic-rag-course`); simple B1–B2 English (`production-agentic-rag-course`); draft issues in `tmp/` before filing (`context-smith`); Claude subscription, not an API key (`job_hunt`). Each one applies to every repo.
- **Stale project state**: an issue-progress note (`on_prem_rag`, issue #78) and a project phase note (`document-xml-mcp`) describe work in progress at one point in time. These should live in the issue, not in memory.
- **Promote to a skill**: the Windows Git Bash path rule (`sir-read-a-lot`) belongs in the `terminal` skill. The `#NNN:` commit subject being stripped by cherry-pick (`job_hunt`) belongs in a git or commit skill.
- Memory is per machine too: the other machine may hold different memories.

## Ideas: verdicts

| # | Idea | Verdict | Rationale |
|---|---|---|---|
| 1 | `session-retro` skill, multi-session | **Pursue, after F3** | Needed, but first test whether `claude-reflect` covers it. Must classify prompts with an LLM (R1). |
| 2 | Friction-event hooks | Park | Transcripts already hold the events. The gaps are retention and the second machine, not capture. job_hunt#75 and #90 cover traces. |
| 3 | Standing-decisions register | **Pursue** (with 7) | R1 and R6 show the same directives repeated across projects. |
| 4 | Backlog triage-closer | **Pursue** | The user already does this by hand ("oldest first", "is this still necessary?", "refine and prioritise"). |
| 5 | Per-skill effectiveness signal | Park | Too little data on this machine: 14 skills, most used once. Revisit with data from both machines. Use usage counts as a rough signal for #37 now. |
| 6 | Mutual-learning digest | Merge into 1 | Same data, same run: an output section of the retro, not a separate tool. |
| 7 | Memory → skill promotion | Merge into 3 | R6 gives the first batch. |
| 8 | PR-review → check generator | Park | Recurring review themes are judgement calls (R2). The few mechanical ones are per-repo lint rules. |
| 9 | Scheduled learning cadence | Park | Do not automate a loop before it has proved useful by hand. |
| 10 | Issue-quality linter | Park | No evidence on this machine, which does not mean the problem is absent. Revisit if a retro finds it. |
| N1 | Finish-work skill (`land-pr`) | **Pursue, highest value** | About 15 prompts in 6 repos ask for the same sequence (R1). |
| N2 | Own-PR review rule | **Pursue (quick win)** | GitHub forbids self-approval; the skill must detect it and choose (F1). |
| N3 | Keep and combine transcripts | **Pursue (human, settings)** | Set `cleanupPeriodDays` explicitly (for example 365) on both machines. Run the miner on each machine and merge only the distilled counts, never raw transcripts. |
| N4 | Workspace preflight (branch, folder, concurrent session) | Merge into N1 | Same moment in the workflow. |
| N5 | Intent prefixes + ask on ambiguity | **Pursue** | R1: questions and corrections look alike; prefixes also label data for the retro (F7). |

## Proposed follow-up issues (drafts, not filed)

Filing waits for review, per the user's preference to see issue drafts first (R6). Suggested order: **F1 → F4**, then F2 and F7, then F3 → F5, then F6.

| ID | Title | Size | Notes |
|---|---|---|---|
| F1 | `[FEAT]: Own-PR review: approve when allowed, else a formal comment review` | S | First slice of F4. Compare the PR author with the current `gh` user. If they differ (bot or other author), submit a formal `--approve`. If they are the same, submit a formal `--comment` review with an explicit verdict line, which still counts as a submitted review ([contributions reference](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)). Read the repo's required-approvals setting to report whether merge needs an admin override. Option for the user to decide: let the agent open PRs under a separate bot identity, so that the user's approval is a real formal approval. |
| F2 | `[FEAT]: Standing-decisions register + promote user-level memories` | S | Ideas 3 and 7. One file of decisions with scope and a revisit trigger. First batch from R6. Human reviews each promotion. |
| F3 | `[SPIKE]: Trial claude-reflect --scan-history against R1 findings` | S | Build-vs-buy for idea 1. Pass: it finds most of the manually found corrections. |
| F4 | `[FEAT]: finish-work skill (land-pr)` | M | N1 and N4. Runs when the user says "I think I'm done". Preflight (branch, folder, concurrent session) → in-depth AI review (`brutally-honest-code-review` / `code-review`) → tool and CI checks → simple AI judgement for trivial items → formal review (F1) → rebase-merge → `branch-cleanup` → watch main with `gh pr checks --watch`, never sleep loops. Each step is conditional on the repo: for example, only run the `dependabot` step where Dependabot is configured. Needs a "how it was tested" section (R2 theme 1). |
| F5 | `[FEAT]: session-retro skill` | M | Ideas 1 and 6. Blocked by F3. LLM-classified corrections, recurrence across ≥2 sessions, a two-column digest (agent errors / human inputs that caused rework). If built, it absorbs `mine_sessions.py` as its bundled script. |
| F6 | `[FEAT]: Backlog triage-closer` | M | Idea 4. Extends the external `triage` skill with "already done?" detection (git log, merged PRs) and close-with-rationale. |
| F7 | `[FEAT]: Intent prefixes (Question:/Correction:/Task:) + ask on ambiguity` | S | N5. Add the convention to the user-level working agreements (F2). The agent asks once when intent is unclear and the difference matters. The retro uses prefixed prompts as labels. |

Human action, no issue: set `cleanupPeriodDays` on both machines (N3).

## Reproduce

```bash
python -I docs/research/scripts/mine_sessions.py                       # counts only
python -I docs/research/scripts/mine_sessions.py --examples tmp/skills/session-learning/examples.json
```

The script is research tooling for this pass, not a skill yet. If F3 ends in "build", it moves into the `session-retro` skill (F5) as a bundled script.
