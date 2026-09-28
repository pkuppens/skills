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

## Relation to skills in this library

- [validation-report-generator](../validation-report-generator/SKILL.md) and [brutally-honest-code-review](../brutally-honest-code-review/SKILL.md) produce **human-review** artefacts: verdicts a human signs off on.
- [dependabot](../dependabot/SKILL.md) reviews and squash-merges only CI-verified patch/minor bumps; major bumps stay with a human.
- [branch-cleanup](../branch-cleanup/SKILL.md) dry-runs first and needs explicit confirmation before `--execute`.
