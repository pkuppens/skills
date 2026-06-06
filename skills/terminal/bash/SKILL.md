---
name: bash
description: >-
  bash syntax for Linux, macOS, WSL2, and Git Bash: quoting, pipelines,
  backslash continuation, hash comments, and copy-paste-safe blocks. Use when
  the detected shell is bash or when writing shell scripts for Unix-like environments.
---

# bash

bash syntax for live commands and shell scripts on Linux, macOS, WSL2, and Git Bash. Activate via [terminal/SKILL.md](../SKILL.md) after context detection.

## Platform notes

| Environment | Signals | Caveats |
|-------------|---------|---------|
| Linux | `uname -s` = Linux | `/bin/bash` vs `/usr/bin/bash` |
| WSL2 | `/proc/version` contains Microsoft | Windows paths via `/mnt/c/` |
| Git Bash | `OSTYPE` often `msys` | Path mixing, slower fork |
| macOS | `uname -s` = Darwin | Default login may be zsh — confirm if bashisms needed |

Details: [platforms.md](references/platforms.md)

## Copy-paste rules (live)

- Comments: `#` only
- Line continuation: `\` as last character on line (no trailing spaces)
- No prose inside fenced blocks
- Prefer `set -euo pipefail` at top of **scripts**, not necessarily one-liner pastes

Multiline example:

```bash
docker run --rm \
  -v "$(pwd):/work" \
  -w /work \
  alpine echo hello
```

## Quoting

| Style | Use |
|-------|-----|
| `'single'` | Literal string |
| `"double"` | Expansion + quotes paths with spaces |
| `$(cmd)` | Command substitution |

```bash
path="/data/my files/readme.md"
cat "$path"
```

## Pipelines and redirection

```bash
command > file.txt
command >> file.txt
command 2>&1 | tee log.txt
command &> all.log
```

## Inspect PATH and commands

```bash
type -a node
which git
echo "$PATH"
command -v python3
```

When `command -v` fails, suggest package manager install or PATH export. Document prereqs in CI/README snippets.

## sudo and elevation

**Default: do not use sudo** in agent-suggested commands.

Offer sudo only when:

- User confirms admin is OK
- Operation genuinely needs root (system packages, `/etc`, low ports)

See [sudo-elevation.md](references/sudo-elevation.md). Always label **Requires sudo** blocks.

## WSL from Windows host

```powershell
wsl.exe -e bash -lc "cd /home/user/proj && npm test"
```

Route shell syntax inside `bash -lc "..."` to bash rules; outer wrapper may be PowerShell or cmd.

## Script header

```bash
#!/usr/bin/env bash
set -euo pipefail
```

## Copy-paste vs documentation

- **Live:** one fence, one target environment when known
- **Docs:** separate **Linux**, **WSL2**, **macOS** sections when install commands differ (apt vs brew)

## Additional resources

- [platforms.md](references/platforms.md)
- [sudo-elevation.md](references/sudo-elevation.md)
