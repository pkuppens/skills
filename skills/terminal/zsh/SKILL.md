---
name: zsh
description: >-
  zsh syntax for live terminal execution on macOS (the default login shell) and
  Linux: where zsh differs from bash — comments in pasted blocks, glob no-match
  errors, word splitting, 1-based arrays, echo escapes, and rehash after installs.
  Use when the detected shell is zsh, when pasted commands fail with "no matches
  found" or "command not found: #", or when writing .zsh scripts or ~/.zshrc edits.
---

# zsh

zsh rules for **live session commands** and **`.zsh` / `~/.zshrc` edits**. Activate via [terminal/SKILL.md](../SKILL.md) after context detection. zsh accepts most bash syntax, so this leaf covers **only the differences**; everything else follows [bash/SKILL.md](../bash/SKILL.md) (quoting, pipelines, redirection, line continuation, sudo).

## Detect

```zsh
echo "${ZSH_VERSION:-not zsh}"
ps -p $$ -o comm=
```

`$SHELL` is the **login** shell, not necessarily the running one. Trust `$ZSH_VERSION` / `ps` over `$SHELL`.

## Paste-breaking differences (live)

| Symptom | Cause | Rule |
|---------|-------|------|
| `zsh: command not found: #` | Interactive zsh treats `#` as a command unless `setopt interactivecomments` is on (off by default, including macOS) | **No comment lines in live paste blocks.** Put explanations outside the fence. |
| `zsh: no matches found: …` | Unmatched glob (`*`, `?`, `[ ]`) is an error (`NOMATCH`), not passed literally as in bash | **Quote** arguments with glob characters: URLs with `?`, `pip install "pkg[extra]"`, `git log "HEAD^"` |
| `zsh: event not found` | `!` history expansion inside double quotes (bash too, interactively) | Use single quotes around text with `!` |
| New binary still "command not found" | zsh caches command paths | `rehash`, or open a new shell |

Multiline paste (no comments inside the fence):

```zsh
curl -fsSL "https://example.com/api?page=1&size=50" \
  -H "Accept: application/json" \
  -o out.json
```

## Syntax differences

| Topic | bash | zsh |
|-------|------|-----|
| Unquoted `$var` with spaces | Split into words | **One** word (`SH_WORD_SPLIT` off) — still quote for portability |
| Array index | `${arr[0]}` first | `${arr[1]}` first (1-based) |
| `echo "a\nb"` | Literal `\n` | Interprets escapes — prefer `printf '%s\n'` |
| Options | `shopt -s …` | `setopt …` / `unsetopt …` |
| PATH edit | `export PATH="$HOME/.local/bin:$PATH"` | Same works; or `path+=("$HOME/.local/bin")` (tied array) |

## Inspect PATH and commands

```zsh
whence -a node
where git
command -v python3
echo "$PATH"
```

## Startup files

| File | Loaded for | Put here |
|------|-----------|----------|
| `~/.zshenv` | Every zsh, including scripts | Rarely anything; keep minimal |
| `~/.zprofile` | Login shells (macOS Terminal tabs) | `eval "$(/opt/homebrew/bin/brew shellenv)"`, PATH |
| `~/.zshrc` | Interactive shells | Aliases, prompt, `setopt`, completions |

After editing: `source ~/.zshrc` (or open a new tab). Append rather than overwrite:

```zsh
printf '%s\n' 'setopt interactivecomments' >> ~/.zshrc
```

## Script authoring

- For **portable repo scripts**, write bash (`#!/usr/bin/env bash`, `.sh`) per [bash/SKILL.md](../bash/SKILL.md); macOS `/bin/bash` is 3.2, so avoid bash 4+ features (associative arrays, `${var,,}`) there.
- For zsh-only scripts (`.zsh`):

```zsh
#!/usr/bin/env zsh
set -euo pipefail
```

## sudo and elevation

Same policy as bash: no sudo by default; label **Requires sudo** blocks. See [sudo-elevation.md](../bash/references/sudo-elevation.md). On macOS, never `sudo brew`.

## Copy-paste vs documentation

- **Live:** one fence, zsh-safe (quoted globs, no comment lines)
- **Docs for macOS readers:** a block that works in zsh **and** bash — quote globs, avoid comments inside paste blocks, avoid arrays
