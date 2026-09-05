# Capability exploration

Every SKILL.md frontmatter field and skill-package feature (Agent Skills
spec + Claude Code extensions), checked against this skill specifically:
adopted with a concrete reason, or explicitly ruled out rather than left
unconsidered. Written once, at design time — not a living doc kept in sync
with the skill.

| Capability | Verdict | Why |
|---|---|---|
| `name` / `description` | **Used** | Required; description carries the trigger phrasing. |
| `disable-model-invocation` | **Personal copy only** | `skills-ref` (this repo's CI gate) validates against the portable Agent Skills spec, which only allows `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` — confirmed by a failed `skills-ref validate` run during implementation. `disable-model-invocation` doesn't travel to Cursor/Codex, so it lives only in the Claude Code-local copy at `~/.claude/skills/dependabot/`; this copy relies on Step 6's confirmation gate instead. |
| `argument-hint` / `arguments` ($repo, $pr_number) | **Personal copy only** | Same portability constraint. The canonical copy resolves the target from prose ("if invoked with a repo or PR number, use it...") instead of named `$`-substitution arguments. |
| `allowed-tools` | **Used, narrowly** | The one Claude Code-only field the spec *does* allow (marked experimental). Pre-approves only the **read-only** `gh` calls (`pr list`, `pr view`, `pr diff`, `pr checks`, `run list`, `run view`, `repo view`). Deliberately excludes `gh pr review` / `gh pr comment` — those stay behind a normal permission prompt because they're the write, visible-to-others step. |
| `disallowed-tools` | **Personal copy only** | Same portability constraint. The canonical copy relies on the "never edit files, only investigate and comment" instruction in Step 4 as prose, not a tool-level block. |
| `compatibility` | **Used** | "Requires the gh CLI authenticated with read and pull-request-review access" — a real requirement, worth declaring for anyone installing this via the Skills CLI into an environment that may not have `gh` set up. |
| Dynamic context injection (`` !`command` ``) | **Considered, not used** | Would be a natural fit for auto-listing open Dependabot PRs at skill-load time. Ruled out because `$repo` is a runtime argument and injected commands can't reliably be parameterized by it before the skill body resolves — an explicit step (Step 1) stays correct for both the default-repo and named-repo invocations; injection would only work for the default case. |
| Executable script (`scripts/classify_bump.py`) | **Used** | Group PRs ("Bump the npm-dev-deps group with 7 updates") bump several packages with no per-package severity in the title. A script gives a reliable numeric-tuple version comparison (`1.9.0`→`1.11.0` is minor, not a downgrade — string comparison gets this wrong) instead of asking the model to eyeball semver diffs. |
| `references/` (review templates) | **Used** | Three review bodies (approve / hold-for-human / CI-investigation) are long enough and reused often enough to disclose rather than inline in SKILL.md. |
| `assets/` | **Not used** | Nothing here is a binary/static resource (image, data file, doc template) distinct from the Markdown templates already covered by `references/`. |
| `context: fork` / `agent` / `background` | **Not used** | The workflow is inherently interactive — it must pause for the user's go-ahead before any `gh pr review` call (Step 6) — and PR counts are small. Forking to a background subagent would remove the human from that confirmation gate, which is the one place this skill can't be autonomous. |
| `model` override | **Not used** | No reasoning-depth mismatch to fix: the default model handles both the mechanical classification steps and the CI root-cause step fine. |
| `effort` override | **Considered, not used** | The classification/CI-check steps are mechanical and would tolerate `low`; the CI-failure investigation (Step 4) wants real reasoning. A single skill-level effort override applies uniformly to both, so it would either under-power the investigation or over-spend on the mechanical steps — no single value fits both. |
| `paths` | **Not used** | Nothing here is triggered by editing a particular file type; it's a PR/CI review workflow, not a file-pattern-triggered one. |
| `hooks` | **Not used** | No session-spanning event to register — the workflow starts and ends within one invocation. |
| `shell` | **Not used (default)** | `gh` behaves identically under bash or PowerShell; no reason to override the default. |
| `license` | **Not used** | No existing skill in `pkuppens/skills` sets a per-skill license; the repo-level `LICENSE` (MIT) already covers it. Adding one here would be the only skill doing so, for no stated reason. |
| `metadata` | **Not used** | No established convention in this repo for what keys to put there yet; nothing to attach. |
| Plugin-skill structure (`plugin.json`, `${CLAUDE_PLUGIN_ROOT}`) | **Not used** | `pkuppens/skills` distributes plain skill directories via the Skills CLI/symlinks, not the plugin format — not this repo's convention. |
| Stacking skills (`/dependabot /other-skill arg`) | **Not used** | No other skill in this library shares state with a PR-triage pass; nothing to compose with. |
| `when_to_use` | **Not used** | Would restate what's already in `description` for a skill this narrow — a no-op field, not additional trigger surface. |
