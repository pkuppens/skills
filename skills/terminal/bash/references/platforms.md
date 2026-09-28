# bash platforms

## Linux

- Shebang: `#!/usr/bin/env bash` or `#!/bin/bash`
- Package managers differ (apt, dnf, pacman) — match distro in docs
- Systemd user services vs system services for admin boundaries

## WSL2

Detect:

```bash
grep -i microsoft /proc/version 2>/dev/null
```

Paths:

```bash
cd /mnt/c/Users/name/project
```

Interop:

- Run from Windows: `wsl -d Ubuntu -e bash -lc 'command'`
- Line endings: watch for CRLF in scripts (`dos2unix` if needed)

Prefer Linux paths inside WSL for repo work under `~` or `/home`.

## Git Bash (MSYS)

- `OSTYPE=msys` or similar
- Prefer Unix-style paths in bash; escape spaces
- Some Windows `.exe` on PATH — `which node` may find `.exe`

## macOS

- Default login shell is often zsh; user may still run bash explicitly
- Homebrew prefix: Apple Silicon `/opt/homebrew`, Intel `/usr/local`
- When `$ZSH_VERSION` is set, route to [zsh/SKILL.md](../../zsh/SKILL.md) instead

## Agent routing

| User context | Action |
|--------------|--------|
| WSL2 detected | bash rules + `/mnt/` path awareness |
| Git Bash on Windows | bash rules + path caution |
| macOS + zsh default | zsh rules ([zsh/SKILL.md](../../zsh/SKILL.md)); bash rules only when the user runs bash explicitly |
