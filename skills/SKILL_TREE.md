# Skill tree

Discoverable index of skills in this library. Keep aligned with folders under `skills/` (one `SKILL.md` per skill directory).

## Meta

| Skill | Path | Purpose |
|-------|------|---------|
| skills-transfer | [skills-transfer/SKILL.md](skills-transfer/SKILL.md) | Install, catalog, derivative skills |
| repo-transfer | [skills-transfer/repo-transfer/SKILL.md](skills-transfer/repo-transfer/SKILL.md) | Land skills tree via PR |

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

## Migration

Additional lifecycle skills migrate from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) per [issue #90](https://github.com/pkuppens/pkuppens/issues/90). See repository issues for status.
