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
- Phase 2 adds zsh leaf; until then ask when `echo $0` shows zsh

## Agent routing

| User context | Action |
|--------------|--------|
| WSL2 detected | bash rules + `/mnt/` path awareness |
| Git Bash on Windows | bash rules + path caution |
| macOS + zsh default | Ask before bash-only syntax, or note zsh Phase 2 |
