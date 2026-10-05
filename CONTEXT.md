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

## Language: legacy refactoring

These terms come from the legacy-refactoring skills and the [`workshops/legacy-refactor/`](workshops/legacy-refactor/README.md) material. Use the plain words in prose; use the term only where a reader needs the precise meaning.

**Oracle** (full form: **test oracle**):
A tool that answers one of two questions about a change: is the change complete, and did the behavior stay the same. Four oracles, from weak to strong: the compiler, a semantic index, tests, and a comparison of produced output files.
_Avoid_: Validator, checker, ground truth. Do not use "oracle" for the AI model — the model proposes, the oracle judges. Do not write "oracle" unqualified where a reader could think of the database vendor; write "test oracle" at first use in a document, and link this entry.

Where the term comes from: **"test oracle" is standard software-testing vocabulary, not a term invented here.** It is normally traced to William Howden's testing work of the late 1970s, and Elaine Weyuker's _On Testing Non-testable Programs_ (The Computer Journal, 1982) is the classic treatment of programs that have no oracle. "The oracle problem" has its own survey: Barr, Harman, McMinn, Shahbaz and Yoo, _The Oracle Problem in Software Testing: A Survey_, IEEE TSE 41(5), 2015.

What this library adds: the literature uses an oracle to judge whether **output** is correct. This library also uses it to judge whether a change is **complete** — the compiler as the oracle for "did I find every call site". That extension is this library's framing. Say so rather than implying it is established.

How the oracle differs by reason for the change:

| Reason | What the oracle must prove | Which step you start on |
| --- | --- | --- |
| Refactor | **Nothing changed.** Every stored output file must stay identical. A changed output file is a failure. | Step 1. The compiler proves you reached every call site. |
| Bug fix | **Exactly one thing changed.** One stored output file changes on purpose; every other file must stay identical. The deliberate change to that one file is the evidence of intent. | Step 3. A bug is rarely a type error, so the compiler cannot see it. |

That difference is the whole reason to name the oracle before you start. Same ladder, different step, and the opposite meaning for a changed output file.

**Oracle ladder**, and a **step** of it:
The four oracles in order of strength. "Climb the ladder" means: use a stronger oracle because the weaker one cannot answer the question. One oracle is one **step**: step 1 is the compiler, step 4 is the comparison of produced output files. Write "oracle step 1" where a document also numbers its own procedure steps.
_Avoid_: Rung (the earlier word in this repository; "step" replaced it everywhere). Pyramid, hierarchy, test pyramid (that is a different idea about test counts).

**Sound (of a search method)**:
A method is sound when it never misses a real result. A text search is not sound. The compiler is sound for the build settings that you actually build.
_Avoid_: Accurate, reliable, correct (these do not say in which direction the method fails).

**Recall**:
The part of the real results that a method found. "Complete recall" means that no place was missed.
_Avoid_: Coverage (that word is already used for test coverage), accuracy.

**Call site**:
One place in the code that calls a specific function or uses a specific member.
_Avoid_: Usage, reference, occurrence (a text search finds occurrences; only some occurrences are call sites).

**Deliberate breakage**:
Breaking an old function on purpose, on a separate branch, so that the compiler stops at every call site and lists them. The list is then complete because of the method, not because somebody was careful.
_Avoid_: Sabotage, hack. Always say "on a branch" — that is what makes it safe.

**Reference output file**:
A stored file that holds the output the code produced before the change. A later run must produce the same bytes. This is the only oracle that catches a change in produced data when the types and the tests stay the same.
_Avoid_: Snapshot test (too broad), golden file (use only when quoting the `golden-output-regression` skill name).

**Intent layer**:
The written record of what legacy code must do: the rules it keeps, the words it uses, and the decisions behind it. In undocumented code it is the first thing an AI agent should produce, before any change.
_Avoid_: Requirements (those are for new work), specification, documentation (too broad).

**Period-correct toolchain**:
A compiler and build system of the same age as the code, usually inside a container, because a current compiler cannot build the old code.
_Avoid_: Legacy toolchain (ambiguous: it can mean an old tool or a tool for old code).

## Example dialogue

**Dev:** I want grill to pick defaults without asking every time.  
**Expert:** Create a **derivative skill** (for example `grill-with-autoaccept`) that tells the agent to read [grill-with-docs](https://github.com/pkuppens/skills) and apply your recommendation policy. Do not edit the canonical grill skill in place.  
**Dev:** How do I add skills from skills.sh?  
**Expert:** Use **skills transfer** — install with the Skills CLI or symlink; record extras in project docs. To contribute back here, use **repo transfer** and open a PR.
