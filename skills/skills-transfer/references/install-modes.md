# Install modes

## Symlink (recommended for this library)

Point the IDE at the **inner** `skills/` folder of a `pkuppens/skills` clone:

```bash
mkdir -p .cursor
ln -s ../pkuppens-skills/skills .cursor/skills
```

Windows: Developer Mode or `mklink /D` — see [repository README](../../../README.md).

## Skills CLI

```bash
npx skills add https://github.com/pkuppens/skills --list -y
npx skills add pkuppens/skills --skill skills-transfer -y
```

| Flag | Effect |
|------|--------|
| (default) | Project scope |
| `-g` | User-global (`~/.cursor/skills/`, etc.) |
| `--copy` | Copy instead of symlink when symlinks fail |
| `-a cursor` | Target specific agents (repeat as needed) |

Record extra packages installed from skills.sh in project `CLAUDE.md` or `docs/skills-used.md`.

## Project vs global

| Scope | Path (typical) | Use when |
|-------|----------------|----------|
| Project | `.cursor/skills/`, `.claude/skills/` | Team baseline in repo |
| Global | `~/.cursor/skills/`, `~/.codex/skills/` | Personal defaults everywhere |

**Side by side:** Canonical tree (symlink) and CLI-installed skills can coexist as siblings; avoid duplicate YAML `name` collisions.

## Child folder layout

If the CLI must own the root, symlink one child (e.g. `.cursor/skills/pkuppens` → clone `skills/`) and keep other installs as siblings.
