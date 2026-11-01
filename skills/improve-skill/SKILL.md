---
name: improve-skill
description: Improves an existing Agent Skill through the pkuppens/skills repo — issue, branch, validator, review by the user and a fresh AI agent, PR — then relinks the personal copy in ~/.claude/skills. Use when the user wants to fix, tighten, or extend a skill, says a skill got something wrong, or invokes /improve-skill.
compatibility: Requires git, the gh CLI, Node.js (npx skills-ref), and a local clone of pkuppens/skills. Windows personal-copy linking needs PowerShell 7+.
---

# Improve a skill

Small skill improvements are frequent, and edits made only in `~/.claude/skills/` drift from the canonical copy. This skill makes the repo the single path: **issue → branch → validate → review → PR → relink**.

## Rules

1. The canonical skill lives in `pkuppens/skills` (`skills/<name>/`). Never edit only the personal copy; if it differs from canonical, canonical wins (Step 6).
2. Every improvement has an issue and a PR. One issue may cover a new skill plus its first use, but not unrelated tweaks.
3. No merge without both reviews (Step 4).

## Steps

### 1. Capture the improvement as evidence

Write down: what the skill did, what it should have done, and the real case that showed it (PR link or anonymised excerpt — no raw transcripts, per the repo rules). Open or reuse an issue:

```bash
gh issue create --repo pkuppens/skills --title "[FEAT]: <verb + object>" --body-file tmp/skills/issue.md --assignee @me
```

**Done when:** the issue states observed vs. expected behaviour and has checkable acceptance criteria.

### 2. Change it in the repo

```bash
cd <clone of pkuppens/skills> && git checkout main && git pull
git checkout -b feature/<issue>-<short-name>
```

Edit `skills/<name>/`. Follow `skills/CLAUDE.md`: `SKILL.md` under ~300 lines (the repo's own limit, tighter than the spec's 500), detail in `references/`, quoted `description` when it has colons. When the skill ships a script, extend its `--self-test`. A behaviour change needs a case that **fails before and passes after** — run it before editing and keep the output.

### 3. Validate

```bash
npx --yes skills-ref validate skills/<name>
claude plugin validate . --strict
```

Both must pass; CI runs the same two commands (ADR 001 in `docs/decisions/` of the repo). Register a new skill in `SKILL_TREE.md` and `.claude-plugin/marketplace.json`. Claude-only frontmatter (`disable-model-invocation`, `disallowed-tools`, `arguments`) is rejected by the validator: keep it in a local overlay, not in canonical (Step 6).

### 4. Review — the user and a separate agent

Both are required, and both are recorded in the PR.

- **Fresh-agent review.** Spawn a new subagent with no conversation history. Give it only the diff (`git diff main -- skills/<name>`), the validator output, and this instruction: fetch the *current* [Claude skill best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) and [Agent Skills specification](https://agentskills.io/specification), then judge the change against them (description triggers, conciseness, progressive disclosure, degrees of freedom, claims without evidence). It reports findings and does not edit. Where subagents are unavailable, put manual steps in the PR instead: a reviewer reads the diff against those two pages and ticks each point.
- **User review.** Show the user the diff and the agent's findings; the user signs off in the PR, not in chat.

Address every finding or reply why not. Re-run Step 3 after changes.

**Done when:** the PR has a comment with the fresh-agent findings and responses, and the user's sign-off (GitHub does not let the PR author approve their own PR, so a review comment or checklist tick counts).

### 5. PR and merge

Commit as `#<issue>: type: description`. The PR body holds: the before/after summary, the failing-then-passing evidence, validator output, the fresh-agent findings with responses, and the manual verification steps (e.g. the Windows link check). Merge only via PR.

**Done when:** the PR is merged and the issue's acceptance criteria are ticked.

### 6. Refresh the personal copy (Windows)

Personal copies let every project use the skill from `~/.claude/skills/`. Use [scripts/link-skill.ps1](scripts/link-skill.ps1); modes and rationale are in [references/windows-linking.md](references/windows-linking.md).

```powershell
pwsh <clone>/skills/improve-skill/scripts/link-skill.ps1 -Name dependabot -Repo <clone> -Mode Junction  # plain skill
pwsh <clone>/skills/improve-skill/scripts/link-skill.ps1 -Name dependabot -Repo <clone> -Mode Overlay   # needs local-only frontmatter
pwsh <clone>/skills/improve-skill/scripts/link-skill.ps1 -Name dependabot -Repo <clone> -Mode Check     # drift report, changes nothing
```

`Junction` needs no admin rights. `Overlay` keeps a real directory whose `SKILL.md` is regenerated from canonical plus `~/.claude/skill-overlays/<name>.yaml`; the other entries are junctions or hard links into the clone. An existing real directory is moved to `~/.claude/skill-backups/`, never deleted (a backup inside `skills/` would load as a second skill).

On macOS/Linux, `ln -s <clone>/skills/<name> ~/.claude/skills/<name>` does the Junction job.

**Done when:** `-Mode Check` reports no drift and an edit in the clone is visible through `~/.claude/skills/<name>`.
