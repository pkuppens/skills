# Skill cooperation patterns

How the skills in this library compose: sequential flows, parallel lenses, and when to trigger each. Every skill named here has a folder under `skills/` — see [SKILL_TREE.md](SKILL_TREE.md) for the index.

## Strategy pipeline (sequential, with a parallel middle)

For a technical request or proposal that needs a CTO-level answer:

```text
request-analyzer → clarification-protocol → delegation-prompt-crafter
  → [parallel lenses]
      architecture-pattern-selector · tech-stack-recommender
      scalability-advisor · cost-estimator
  → [parallel challenge]
      antipattern-detector · assumption-challenger
  → validation-report-generator
```

1. [request-analyzer](request-analyzer/SKILL.md) classifies the request and flags vague requirements.
2. [clarification-protocol](clarification-protocol/SKILL.md) turns the gaps into targeted questions. Skip when nothing is missing.
3. [delegation-prompt-crafter](delegation-prompt-crafter/SKILL.md) structures the handoff when specialist agents do the analysis.
4. The four lenses — [architecture-pattern-selector](architecture-pattern-selector/SKILL.md), [tech-stack-recommender](tech-stack-recommender/SKILL.md), [scalability-advisor](scalability-advisor/SKILL.md), [cost-estimator](cost-estimator/SKILL.md) — are independent and can run in parallel. Use only the ones the question needs.
5. [antipattern-detector](antipattern-detector/SKILL.md) and [assumption-challenger](assumption-challenger/SKILL.md) challenge the draft answer in parallel.
6. [validation-report-generator](validation-report-generator/SKILL.md) produces the verdict.

Then, when the plan is accepted: [roadmap-generator](roadmap-generator/SKILL.md) breaks it into epics, stories and tasks.

[ml-cv-specialist](ml-cv-specialist/SKILL.md) is an independent domain lens: add it to step 4 for ML/CV work.

## Code review

[brutally-honest-code-review](brutally-honest-code-review/SKILL.md) is standalone. On design-level findings it can pull in [antipattern-detector](antipattern-detector/SKILL.md) and [assumption-challenger](assumption-challenger/SKILL.md), and summarise with [validation-report-generator](validation-report-generator/SKILL.md).

## Terminal routing

Any skill that emits shell commands should follow [terminal](terminal/SKILL.md), which detects the shell (project docs → runtime probe → ask) and routes to one leaf: [cmd](terminal/cmd/SKILL.md), [powershell](terminal/powershell/SKILL.md), [bash](terminal/bash/SKILL.md) or [zsh](terminal/zsh/SKILL.md). Load only the leaf for the detected shell.

## Repo maintenance (after merges)

```text
PR merged → branch-cleanup (dry-run → confirm → --execute)
Dependabot PRs open → dependabot → branch-cleanup
```

- [dependabot](dependabot/SKILL.md) reviews and squash-merges CI-verified patch/minor bumps; majors go to a human.
- [branch-cleanup](branch-cleanup/SKILL.md) then removes the merged branches, local and remote.

## Documentation

[readme-authoring](readme-authoring/SKILL.md) is standalone. Pair it with [terminal](terminal/SKILL.md) so the README's commands are copy-paste safe for the project's shells.

## Agent orchestration

[ai-factory](ai-factory/SKILL.md) sets up a supervisor + subagent swarm. Its subagents can run the strategy pipeline above; confidential steps stay on the local model.

## Growing this library

```text
need a skill → search public skills first → skills-transfer (install/adapt)
             → or skill-creation (author) → repo-transfer (land via PR)
```

- [skill-creation](_meta/skill-creation/SKILL.md) — authoring rules; install before authoring.
- [skills-transfer](skills-transfer/SKILL.md) — install or adapt existing skills; [repo-transfer](skills-transfer/repo-transfer/SKILL.md) lands a tree in this repo via PR.
- [_meta/human-ai-execution.md](_meta/human-ai-execution.md) — which steps an agent may do alone, and which need a human.

## Trigger conditions

| When | Trigger |
|------|---------|
| Vague or broad technical request | request-analyzer |
| Choosing architecture, stack, scale or budget | the matching lens from the strategy pipeline |
| Reviewing a proposal or plan | antipattern-detector + assumption-challenger → validation-report-generator |
| Accepted plan needs a backlog | roadmap-generator |
| Reviewing code | brutally-honest-code-review |
| Emitting shell commands or scripts | terminal |
| Writing or auditing a README | readme-authoring |
| Dependabot PRs open | dependabot |
| After a PR merge | branch-cleanup |
| Need a new skill | skills-transfer or skill-creation |
