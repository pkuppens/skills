# Skill tree

Discoverable index of skills in this library. Keep aligned with folders under `skills/` (one `SKILL.md` per skill directory).

## Meta

| Skill | Path | Purpose |
|-------|------|---------|
| skills-transfer | [skills-transfer/SKILL.md](skills-transfer/SKILL.md) | Install, catalog, derivative skills |
| repo-transfer | [skills-transfer/repo-transfer/SKILL.md](skills-transfer/repo-transfer/SKILL.md) | Land skills tree via PR |

## Repo maintenance

| Skill | Path | Purpose |
|-------|------|---------|
| branch-cleanup | [branch-cleanup/SKILL.md](branch-cleanup/SKILL.md) | Fetch/prune, fast-forward, and delete merged local+remote git branches |
| dependabot | [dependabot/SKILL.md](dependabot/SKILL.md) | Triage open Dependabot PRs: classify semver severity, verify CI, post formal reviews for CI-verified patch/minor bumps |

## Language and framework skills

| Skill | Path | Purpose |
|-------|------|---------|
| terminal | [terminal/SKILL.md](terminal/SKILL.md) | Multi-OS terminal orchestration: live execution and shell script authoring (.bat, .ps1, .sh), context detection, copy-paste-safe commands |
| cmd | [terminal/cmd/SKILL.md](terminal/cmd/SKILL.md) | Windows cmd.exe and batch files (replaces external batch-files) |
| powershell | [terminal/powershell/SKILL.md](terminal/powershell/SKILL.md) | PowerShell 5.1 and 7+ |
| bash | [terminal/bash/SKILL.md](terminal/bash/SKILL.md) | bash on Linux, macOS, WSL2, Git Bash |

### Terminal tree (nested)

```text
terminal/
├── SKILL.md              # orchestrator
├── references/
├── cmd/SKILL.md
├── powershell/SKILL.md
└── bash/SKILL.md
```

Phase 2 (Epic #10): `terminal/zsh/`, expanded `references/terminal-emulators.md`.

## Documentation skills

| Skill | Path | Purpose |
|-------|------|---------|
| readme-authoring | [readme-authoring/SKILL.md](readme-authoring/SKILL.md) | Create, review, and rewrite READMEs — covers getting the code, prerequisites, and dev-mode run instructions as first-class sections |

## Strategy and lifecycle skills

| Skill | Path | Purpose |
|-------|------|---------|
| tech-stack-recommender | [tech-stack-recommender/SKILL.md](tech-stack-recommender/SKILL.md) | Recommend tech stacks based on project requirements/constraints |
| architecture-pattern-selector | [architecture-pattern-selector/SKILL.md](architecture-pattern-selector/SKILL.md) | Select architecture patterns (monolith, microservices, modular monolith, serverless) |
| scalability-advisor | [scalability-advisor/SKILL.md](scalability-advisor/SKILL.md) | Scale guidance across 0-1 to 10M+ users with architecture recommendations per stage |
| cost-estimator | [cost-estimator/SKILL.md](cost-estimator/SKILL.md) | TCO and budget projections for technology decisions |
| roadmap-generator | [roadmap-generator/SKILL.md](roadmap-generator/SKILL.md) | Epic/story/task breakdown with effort estimates and validation checkpoints |
| delegation-prompt-crafter | [delegation-prompt-crafter/SKILL.md](delegation-prompt-crafter/SKILL.md) | Structure prompts for specialist agent handoff |
| request-analyzer | [request-analyzer/SKILL.md](request-analyzer/SKILL.md) | Classify technical requests and identify vague requirements |
| clarification-protocol | [clarification-protocol/SKILL.md](clarification-protocol/SKILL.md) | Generate targeted questions for missing context |
| antipattern-detector | [antipattern-detector/SKILL.md](antipattern-detector/SKILL.md) | Detect structural anti-patterns in proposals and architectures |
| assumption-challenger | [assumption-challenger/SKILL.md](assumption-challenger/SKILL.md) | Surface implicit assumptions and wishful thinking |
| brutally-honest-code-review | [brutally-honest-code-review/SKILL.md](brutally-honest-code-review/SKILL.md) | Evidence-first code review with certainty levels |
| validation-report-generator | [validation-report-generator/SKILL.md](validation-report-generator/SKILL.md) | Produce structured 8-section validation reports with verdicts |
| ml-cv-specialist | [ml-cv-specialist/SKILL.md](ml-cv-specialist/SKILL.md) | ML/CV expertise patterns and model selection guidance |

### Strategy pipeline (sequential flow)

```text
request-analyzer -> clarification-protocol -> delegation-prompt-crafter
       |                                              |
       v                                              v
architecture-pattern-selector  tech-stack-recommender  scalability-advisor  cost-estimator
                    \                /          |            |             /
                     \              /           |            |            /
                  antipattern-detector  assumption-challenger     (parallel analysis)
                              \                   /
                               v                 v
                      brutally-honest-code-review validation-report-generator

ml-cv-specialist — independent domain-specific skill
```

## Migration

- [issue #13](https://github.com/pkuppens/skills/issues/13): Epic — Migrate all 13 personal skills from local `~/.claude/skills/` to pkuppens/skills (in progress via PR)
- `readme-authoring` migrated from `~/.cursor/skills/readme-authoring` (local-only, not yet symlinked to a shared source), extended with explicit getting-the-code / prerequisites / dev-server-vs-deploy guidance and GFM admonition usage inspired by GitHub's `create-readme` skill
- Additional lifecycle skills migrate from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) per [issue #90](https://github.com/pkuppens/pkuppens/issues/90). See repository issues for status.
