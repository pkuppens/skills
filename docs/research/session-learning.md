# Session learning: findings (first pass)

Issue: [#43](https://github.com/pkuppens/skills/issues/43). Date: 2026-10-11. Status: **first pass, for review**. Verdicts are provisional: they hold until new evidence contradicts them.

This document contains no raw transcript text. Quotes from prompts are short paraphrases. Personal, non-code sessions appear only as counts.

## Summary

- The local evidence base is **small and recent**: 58 sessions, 112 human prompts, 3,213 tool calls, almost all from September–October 2026.
- **Keyword detection of corrections does not work for this user.** It found 1 correction in 112 prompts. Reading the prompts by hand found about 8. Corrections come as a constraint inside the next instruction ("do this on the branch you left open", "don't solve this with retries"), not as "no, wrong". Any retro tool has to classify prompts with an LLM.
- **The biggest repeated cost is one procedure, not one error.** About 15 prompts across 6 repos ask for the same "land the PR" sequence: review, formal review comment, rebase-merge, branch cleanup, watch main. The two most-used skills (`branch-cleanup`: 21 uses, `dependabot`: 11) are parts of it.
- **User-level preferences are stuck in project memory.** Five preferences that apply everywhere are each saved in only one project's memory. Example: "draft issues in `tmp/` before filing" lives in `context-smith` memory, so this session filed #43 directly, against that preference.
- **A WikiSkill loop already exists in `job_hunt`** (epic [job_hunt#70](https://github.com/pkuppens/job_hunt/issues/70), ADR [job_hunt#71](https://github.com/pkuppens/job_hunt/issues/71) closed). #37 should start from that ADR, not from zero.
- Tool errors are rare (121 of 3,213 calls, 3.8%) and mostly harmless exploration (probing for files that do not exist). They are not the main source of rework.

## Prerequisites and related work

#43 has **no blocking prerequisites**. Related work:

| Item | Relation |
|---|---|
| [#37](https://github.com/pkuppens/skills/issues/37) WikiSkill spike | Consumes R1 and idea 5 here (the per-skill signal it calls the hard part). |
| [job_hunt#70](https://github.com/pkuppens/job_hunt/issues/70) WikiSkill epic | Sibling implementation. #71 ADR and #72 scaffold are closed; #75 (raw trace capture) and #90 (Langfuse trace → raw) are open. |
| [job_hunt#82](https://github.com/pkuppens/job_hunt/issues/82) | Decided on ADR length-budget checks: the "context economy" theme in R2. |

## R1: Session archaeology

Method: [scripts/mine_sessions.py](scripts/mine_sessions.py) parses `~/.claude/projects/**/*.jsonl` and prints counts only. Raw snippets go to the gitignored `tmp/` when `--examples` is passed. After that, the 112 prompts were read by hand.

### Counts

| Signal | Count |
|---|---|
| Sessions (incl. 8 subagent files) | 58 |
| Human prompts | 112 |
| Tool calls | 3,213 |
| Tool errors | 121 (3.8%; 99 of them Bash) |
| User interrupts | 3 |
| Keyword-detected corrections | 1 |
| Files edited 5+ times in one session | 14 |
| Date range | 2026-06-17 to 2026-10-11; over 95% of records are from Sep–Oct |

Tool errors by class: nonzero exit (43), test/lint failure (31), file not found (20), permission denied (10), input validation (4), blocked by the harness (4), other (9).

### Failure classes worth acting on

| Class | Evidence | Kind |
|---|---|---|
| **Approving your own PR** | The user often asks for a "formal review approval" on their own PRs. GitHub rejects this (`Can not approve your own pull request`), and the auto-mode classifier blocked it twice as "Self-Approval". | Mechanical: a standing rule |
| **Wrong branch or folder** | 3 prompts in 2 repos had to restate the branch ("from the correct branch", "on the branch you left open"). In one more case two sessions worked in the same folder. | Mechanical: a preflight check |
| **Retries instead of a root cause** | The agent retried an API error. The user said retries would not help and asked for a small prototype first. The fix was a request bug. | Judgement: `diagnosing-bugs` |
| **Sleep-polling CI** | 2 sleep-and-check chains blocked by the harness ("use Monitor"). | Mechanical: skill text |
| **Windows shell quirks** | Python Store alias, heredoc quote errors, "command line too long", JSON-escaping of `C:\` paths in tool input (2). | Mechanical: `terminal` skill |
| **"Could lint have caught this?"** | The user asked this after an undefined-function bug. | Mechanical: per-repo lint rule |

### Manually found corrections (paraphrased)

Restate the branch (×3) · don't fix with retries · write a prototype first · the PR still has leftovers, commit and push · is this setup option verified? · could a lint step have caught this earlier? · a factual correction to a claim the agent made about the user.

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
| WikiSkill (#37, job_hunt#71) | A persistent wiki of failure causes survives even when a skill edit is rolled back; gate edits on a measured signal. |
| Voyager (skill library) | A skill joins the library only after it has worked in execution. This matches R2 theme 1, "show that it works". |
| Reflexion | Verbal self-reflection stored per episode; useful inside a session, weak across sessions. |
| Dynamic Cheatsheet | Memory that adapts at test time; ACE builds on it. |

## R6: Memory audit

13 project memory folders, 27 files. Findings:

- **User-level facts saved in one project only**: minimal responses and lean docs (`on_prem_rag`); formal PR reviews count toward the contribution streak (`production-agentic-rag-course`); simple B1–B2 English (`production-agentic-rag-course`); draft issues in `tmp/` before filing (`context-smith`); Claude subscription, not an API key (`job_hunt`). Each one applies to every repo.
- **Stale project state**: an issue-progress note (`on_prem_rag`, issue #78) and a project phase note (`document-xml-mcp`) describe work in progress at one point in time. These should live in the issue, not in memory.
- **Promote to a skill**: the Windows Git Bash path rule (`sir-read-a-lot`) belongs in the `terminal` skill. The `#NNN:` commit subject being stripped by cherry-pick (`job_hunt`) belongs in a git or commit skill.

## Ideas: verdicts

| # | Idea | Verdict | Rationale |
|---|---|---|---|
| 1 | `session-retro` skill, multi-session | **Pursue, after F3** | Needed, but first test whether `claude-reflect` covers it. Must classify prompts with an LLM (R1). |
| 2 | Friction-event hooks | Park | Transcripts already hold the events; the problem is retention, not capture. job_hunt#75 and #90 cover traces. |
| 3 | Standing-decisions register | **Pursue** (with 7) | R1 and R6 show the same directives repeated across projects. |
| 4 | Backlog triage-closer | **Pursue** | The user already does this by hand ("oldest first", "is this still necessary?", "refine and prioritise"). |
| 5 | Per-skill effectiveness signal | Park | Too little data: 14 skills, most used once. Revisit when retention is fixed. Use usage counts as a rough signal for #37 now. |
| 6 | Mutual-learning digest | Merge into 1 | Same data, same run: an output section of the retro, not a separate tool. |
| 7 | Memory → skill promotion | Merge into 3 | R6 gives the first batch. |
| 8 | PR-review → check generator | Park | Recurring review themes are judgement calls (R2). The few mechanical ones are per-repo lint rules. |
| 9 | Scheduled learning cadence | Park | Do not automate a loop before it has proved useful by hand. |
| 10 | Issue-quality linter | Close | No evidence that issue shape caused rework. Revisit if a retro finds it. |
| N1 | `land-pr` skill | **Pursue** | About 15 prompts in 6 repos ask for the same sequence (R1). |
| N2 | Own-PR review rule | **Pursue (quick win)** | GitHub and the classifier both block self-approval (R1). |
| N3 | Keep transcripts longer | **Pursue (human, settings)** | The evidence base is about 6 weeks deep. Set `cleanupPeriodDays` in user settings explicitly (for example 365). |
| N4 | Workspace preflight (branch, folder, concurrent session) | Merge into N1 | Same moment in the workflow. |

## Proposed follow-up issues (drafts, not filed)

Filing waits for review, per the user's preference to see issue drafts first (R6).

| ID | Title | Size | Notes |
|---|---|---|---|
| F1 | `[FEAT]: Own-PR review rule: comment-review, never self-approve` | S | Quick win. Update `skills/_meta/human-ai-execution.md`, and any skill that reviews the user's own PRs, to post `gh pr review --comment` with a verdict. `--approve` stays for bot PRs (`dependabot`). |
| F2 | `[FEAT]: Standing-decisions register + promote user-level memories` | S | Ideas 3 and 7. One file of decisions with scope and a revisit trigger. First batch from R6. Human reviews each promotion. |
| F3 | `[SPIKE]: Trial claude-reflect --scan-history against R1 findings` | S | Build-vs-buy for idea 1. Pass: it finds most of the manually found corrections. |
| F4 | `[FEAT]: land-pr skill` | M | N1 and N4: preflight (branch, folder, concurrent session) → review → formal review comment → rebase-merge → `branch-cleanup` → watch main with `gh pr checks --watch`, never sleep loops. Requires a "how it was tested" section (R2 theme 1). |
| F5 | `[FEAT]: session-retro skill` | M | Ideas 1 and 6. Blocked by F3. LLM-classified corrections, recurrence across ≥2 sessions, a two-column digest (agent errors / human inputs that caused rework). |
| F6 | `[FEAT]: Backlog triage-closer` | M | Idea 4. Extends the external `triage` skill with "already done?" detection (git log, merged PRs) and close-with-rationale. |

Human action, no issue: set `cleanupPeriodDays` (N3).

## Reproduce

```bash
python -I docs/research/scripts/mine_sessions.py                       # counts only
python -I docs/research/scripts/mine_sessions.py --examples tmp/skills/session-learning/examples.json
```
