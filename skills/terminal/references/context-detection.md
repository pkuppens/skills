# Context detection

Resolve shell, OS, terminal emulator, and admin expectations before writing commands.

## Detection order

Apply sources **top to bottom**. Stop at the first confident match unless a lower source is marked as override.

| Priority | Source | Signals |
|----------|--------|---------|
| 1 | `.devcontainer/devcontainer.json` | `features`, `postCreateCommand`, `remoteUser`, `customizations.vscode.settings` |
| 2 | CI workflow YAML | `jobs.*.runs-on`, `defaults.run.shell`, step `shell:` key |
| 3 | `.vscode/settings.json` | `terminal.integrated.defaultProfile.windows/linux/osx`, profile `path` and `args` |
| 4 | README **Development environment** block | Structured fields (see below) |
| 5 | Runtime probe | Active session indicators (see below) |
| 6 | Ask user | When doc intent conflicts with probe |

### Machine-readable vs README

Machine-readable sources (devcontainer, CI, VS Code settings) **win by default**.

The README block wins only when it includes an explicit override line, for example:

```markdown
- **Override machine defaults:** yes
```

## Development environment block (optional README)

Projects may declare intent in README or CONTRIBUTING:

```markdown
## Development environment
- **OS:** windows | linux | macos | wsl2
- **Shell:** cmd | powershell | bash | zsh
- **Terminal:** windows-terminal | wezterm | iterm2 | alacritty | ghostty | kitty | cmux | tmux | zellij
- **Admin:** rarely | sometimes | wsl-only
- **Override machine defaults:** no
```

Parse field values case-insensitively. Unknown terminal values → note in response; check [terminal-emulators.md](terminal-emulators.md).

## Runtime probe

Inspect the active execution environment when docs are silent or for conflict checks.

| Shell | Probe commands / signals |
|-------|--------------------------|
| cmd | `%ComSpec%` ends with `cmd.exe`; no `$PSVersionTable` |
| PowerShell | `$PSVersionTable.PSVersion`; `$PSVersionTable.PSEdition` (`Desktop` = 5.1, `Core` = 7+) |
| bash | `$BASH_VERSION` set; `$0` or `$SHELL` contains `bash` |
| WSL2 | `/proc/version` contains `Microsoft` or `WSL`; `wsl.exe -l -v` from Windows host |
| macOS | `uname` = `Darwin`; default login shell often zsh (Phase 2 leaf — confirm with user in Phase 1) |

Also note:

- Current working directory and repo path (Windows vs Unix roots)
- Whether the session appears elevated (see leaf admin references)

## Conflict rule

When **documented shell ≠ probed shell**, **ask the user** which to target. Example:

- README: `Shell: powershell`
- Probe: `ComSpec=C:\Windows\System32\cmd.exe`

Do not silently pick one. Offer:

1. Commands for documented shell (user runs in that profile)
2. Commands for active probe shell (works in current session)

## Routing after detection

| Detected shell | Leaf skill |
|----------------|------------|
| cmd | [../cmd/SKILL.md](../cmd/SKILL.md) |
| powershell | [../powershell/SKILL.md](../powershell/SKILL.md) |
| bash | [../bash/SKILL.md](../bash/SKILL.md) |
| wsh / unclear | Ask user |

## Terminal emulator detection

Emulator affects tabs and paste UX, not shell grammar. Read declared **Terminal:** from README or settings when present. See [terminal-emulators.md](terminal-emulators.md).
