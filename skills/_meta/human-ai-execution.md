# Human vs AI execution (issues and skills)

Use this note when scoping GitHub issues and when agents follow skills that affect **judgment**, **sign-off**, or **compliance**.

## Triage labels (this repo)

This repo uses the five canonical triage roles. The mapping lives in [docs/agents/triage-labels.md](../../docs/agents/triage-labels.md).

| Label | When to use |
|-------|-------------|
| `ready-for-agent` | Fully specified; an agent may execute end-to-end (drafting Markdown, scaffolding, link checks, skill edits). Human merge review is still normal: agents open PRs, humans merge. |
| `ready-for-human` | A human must perform or decide the step (stakeholder decision, regulatory interpretation, production change approval). An agent may still draft. |
| `needs-info` | Waiting on the reporter; don't start. |
| `needs-triage` | Not yet evaluated. |
| `wontfix` | Will not be actioned. |

## Issue body template (optional)

Add an **Execution** block when one issue mixes agent and human steps, so ownership stays with the issue:

```markdown
## Execution
- [ ] (agent) …
- [ ] (human-review) … agent drafts, human approves
- [ ] (human) …
```

## External skills

Some workflow steps rely on skills **not in this repo**. Install them separately via the [Skills CLI](https://github.com/vercel-labs/skills) or [skills.sh](https://www.skills.sh/); conventions are in the [README § External and vendor skills](../../README.md#external-and-vendor-skills).

| Skill | Role in this workflow | Reference |
|-------|----------------------|-----------|
| **triage** | Classify issues, post an agent brief, apply `ready-for-agent` / `ready-for-human` | <https://www.skills.sh/mattpocock/skills/triage> |
| **grill-with-docs** | Sharpen vague requirements against `CONTEXT.md`; produce acceptance criteria before coding | <https://www.skills.sh/mattpocock/skills/grill-with-docs> |

## Approval rule for merging

A PR merges only with **approval and green CI on the same head commit**. The approval is a formal `APPROVE` review, never a chat message. It may come from the user or from the agent; an agent approves only after the chores are done (review findings fixed or filed, CI checked) and names the SHA it verified. Any push after the approval needs a new one.

The agent cannot approve a PR its own `gh` login opened: GitHub rejects self-approval. Until agent PRs are opened by a bot identity ([#45](https://github.com/pkuppens/skills/issues/45)), such a PR waits for the user: a comment review by the user on the head commit whose body clearly approves counts as the approval. The agent shares the user's login, so anything it posts carries a marker and never counts, and it never posts an approving comment review itself. Without such a review the PR is not merged. The commands that check the rule: [finish-work/references/merge-gate.md](../finish-work/references/merge-gate.md).

## Relation to skills in this library

- [validation-report-generator](../validation-report-generator/SKILL.md) and [brutally-honest-code-review](../brutally-honest-code-review/SKILL.md) produce **human-review** artefacts: verdicts a human signs off on.
- [finish-work](../finish-work/SKILL.md) applies the approval rule above to one PR, end to end.
- [dependabot](../dependabot/SKILL.md) reviews and rebase-merges only CI-verified patch/minor bumps; major bumps stay with a human.
- [branch-cleanup](../branch-cleanup/SKILL.md) dry-runs first and needs explicit confirmation before `--execute`.
