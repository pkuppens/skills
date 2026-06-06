# Alternative shells

Not first-class sub-skills in Phase 1. Use when user names fish, `sh`, or another shell.

## fish

- Comments: `#`
- Continuation: `\` at end of line
- No bash-style `$(…)` in older fish — prefer `fish -c` only when user confirms fish
- PATH: `fish -c 'echo $PATH'`

## POSIX sh

- Prefer explicit `#!/bin/sh` when writing scripts for `/bin/sh` targets
- Avoid bashisms (`[[ ]]`, `{a,b}` expansion) unless script is bash-only

## When to ask

If detection is ambiguous between bash and zsh on macOS, ask before using bash-specific syntax. zsh leaf skill arrives in Phase 2 (#10).

## Routing default

When user says "shell script" without naming fish/sh, route to [bash/SKILL.md](../bash/SKILL.md) after context detection.
