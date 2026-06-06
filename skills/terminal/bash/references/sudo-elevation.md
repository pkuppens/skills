# sudo and elevation (bash)

**Default: no sudo** in agent commands. Non-root first.

## When sudo may be needed

- System package install (`apt install`, `dnf install`)
- Writing `/etc/*`, `/usr/local` without user-owned alt
- Binding ports < 1024

## Prefer non-root alternatives

| Need | Alternative |
|------|-------------|
| User CLI tool | `~/.local/bin`, `npm -g` with nvm/fnm user prefix |
| Project deps | `./venv`, `node_modules/.bin`, `cargo install --path` |
| Docker | User in `docker` group (document group add as admin one-time step) |

## Offer sudo explicitly

Label block:

```bash
# Requires sudo — installs system package
sudo apt-get update && sudo apt-get install -y jq
```

Do not combine sudo commands with unrelated work in one paste without user consent.

## Detect if already root

```bash
id -u
# 0 = root
```

If root, drop `sudo` from suggestions.

## macOS

Prefer `brew install` without sudo when Homebrew is user-owned. System `/usr/bin/sudo` still needed for some legacy installs — document exception.

## WSL

`sudo` inside WSL is separate from Windows Admin. WSL default user often has passwordless sudo — still ask before using.

## Agent rules

1. Never assume passwordless sudo
2. Warn that sudo commands are irreversible on system paths
3. For CI snippets, use container/root as appropriate — label **CI only**
