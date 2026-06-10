# pkuppens/skills

Canonical Agent Skills library for Cursor, Claude, and Codex. This file is the domain glossary only (no implementation detail).

## Language

**Skill library**:
The `pkuppens/skills` repository: portable `SKILL.md` trees under `skills/`, validated in CI.
_Avoid_: App, product, monorepo (for this repo alone).

**Catalog**:
The discoverable index of skills in this library (`SKILL_TREE.md`, README pointers) plus optional curated bundles and optional listing on skills.sh.
_Avoid_: Package registry (unless referring to npm skills CLI).

**Skills transfer**:
The meta-workflow for bringing skills from external sources into a consumer environment or into this library.
_Avoid_: Migration (use only for the pkuppens/pkuppens epic), deploy.

**Repo transfer**:
The sub-workflow for landing a whole skills directory tree into this skill library with correct layout and pull-request hygiene.
_Avoid_: Repo clone, git pull.

**Derivative skill**:
A new skill folder that builds on one or more existing skills by reference (for example a variant that auto-accepts recommendations instead of asking each time). The base skill stays canonical; the derivative documents its delta.
_Avoid_: Fork (unless the whole skill is copied and owned locally), override file.

**Consumer install**:
Linking or installing skills into IDE paths (project-scoped or user-global) via symlink or Skills CLI.
_Avoid_: Deploy, publish (unless pushing to GitHub or skills.sh).

**Canonical skill**:
A skill maintained in this repository under `skills/<name>/`, treated as the source of truth for that topic in the library.
_Avoid_: Vendor skill, upstream (for skills only installed via `npx skills add` elsewhere).

**Terminal skill tree**:
The nested `skills/terminal/` skills: an orchestrator routes work to shell-specific leaves (cmd, powershell, bash, zsh) so agents load only the syntax context they need.
_Avoid_: Shell skill (too generic), batch-files (superseded by `terminal/cmd` in this library).

**Shell sub-skill**:
A leaf skill under `terminal/` that owns command syntax, copy-paste rules, and elevation patterns for one shell (for example `terminal/powershell/`).
_Avoid_: Terminal emulator, OS.

**Development environment block**:
An optional README section where a project declares OS, shell, terminal emulator, and admin expectations so agents prefer team intent over runtime guesses.
_Avoid_: Devcontainer spec (machine-readable source that may override or complement the block), `.env`.

**Terminal emulator**:
The host application that wraps shell sessions (tabs, splits, copy-paste behavior). Examples: Windows Terminal on Windows (tabs over cmd or PowerShell), [cmux](https://cmux.com/) on macOS (multiplexer like tmux on Linux), iTerm2, WezTerm, Alacritty.
_Avoid_: Shell (cmd, bash), OS, terminal multiplexer when used only as a protocol (unless the user names the emulator).

## Example dialogue

**Dev:** I want grill to pick defaults without asking every time.  
**Expert:** Create a **derivative skill** (for example `grill-with-autoaccept`) that tells the agent to read [grill-with-docs](https://github.com/pkuppens/skills) and apply your recommendation policy. Do not edit the canonical grill skill in place.  
**Dev:** How do I add skills from skills.sh?  
**Expert:** Use **skills transfer** — install with the Skills CLI or symlink; record extras in project docs. To contribute back here, use **repo transfer** and open a PR.
