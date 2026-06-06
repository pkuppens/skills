---
name: terminal
description: >-
  Routes terminal work to the correct shell sub-skill and enforces copy-paste-safe
  command blocks across OS and terminal types. Detects context from project docs and
  runtime probes. Use when running terminal commands, writing shell scripts, preparing
  CI snippets, working with Windows CMD, PowerShell, bash, WSL2, multiline commands,
  pipes, redirects, admin elevation, PATH issues, or copy-paste command blocks.
---

# Terminal

Orchestrates multi-OS terminal command work by detecting shell context, loading the matching **shell sub-skill**, and enforcing copy-paste-safe output.

## When to use

- Run or suggest commands in the user's shell session
- Author `.bat`, `.cmd`, `.ps1`, or shell scripts
- Write README, CONTRIBUTING, or CI command snippets
- Debug "command not found", wrong quoting, or broken multiline paste
- Choose admin vs non-admin command variants on Windows or Unix

## Flow

1. **Detect context** — follow [context-detection](references/context-detection.md) (docs → probe → ask on conflict).
2. **Route to leaf skill** — read the matching sub-skill before writing commands:
   - Windows cmd.exe → [cmd/SKILL.md](cmd/SKILL.md)
   - PowerShell → [powershell/SKILL.md](powershell/SKILL.md)
   - bash (Linux, macOS, WSL2, Git Bash) → [bash/SKILL.md](bash/SKILL.md)
   - zsh → Phase 2 (not yet in this library); use bash rules only when user confirms zsh is acceptable
3. **Apply copy-paste rules** (below).
4. **Prefer non-admin** — detect elevation; offer elevated variants only when required. Never silently assume admin.

## Copy-paste rules

### Live execution (agent runs command or user pastes once)

- One fenced block, **one shell**, runnable **as-is**
- No prose, placeholders, or `$VAR` explanations inside the fence
- Use the leaf skill's comment character and line continuation
- Match the detected shell — do not mix `#` bash comments with `REM` cmd in one block

### Documentation and CI (context unknown or multi-audience)

- Use **labeled sections** per shell when target is unknown, for example `**PowerShell**`, `**CMD**`, `**bash**`
- Each section gets its own fenced block
- When project docs declare a single shell, one block is enough

## Terminal emulators

Emulator choice (tabs, multiplexer, paste quirks) is **not** a separate skill. See [terminal-emulators](references/terminal-emulators.md) when the user names an emulator or README declares one. Emulator does not change shell syntax — route to the shell leaf.

## Environment and PATH

When a command fails with "not found":

1. Use the leaf skill's inspect commands (`where.exe`, `Get-Command`, `which`/`type`)
2. Suggest a fix (PATH entry, package install, correct binary name)
3. For docs/CI, document prerequisites explicitly (`export PATH=…`, install step)

## Alternative shells

fish, POSIX `sh`, and other shells: see [alternative-shells](references/alternative-shells.md). Do not assume bash syntax without confirmation.

## Replaces external batch-files

The `batch-files` vendor skill is superseded by [cmd/SKILL.md](cmd/SKILL.md) in this library. Uninstall external `batch-files` after adopting `terminal/cmd`.

## Additional resources

- [context-detection.md](references/context-detection.md)
- [terminal-emulators.md](references/terminal-emulators.md)
- [alternative-shells.md](references/alternative-shells.md)
