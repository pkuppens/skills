# Unified AI coding skills

Canonical **Agent Skills** library for Cursor, Claude, and Codex: arc42-aligned workflows from ideation through operations. GitHub profile narrative stays in [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens); **this repository is the skills-only home.**

**Quick links:** [skills/SKILL_TREE.md](skills/SKILL_TREE.md) (full index; populated as migration PRs land) · [skills/COOPERATION.md](skills/COOPERATION.md) · [skills/CLAUDE.md](skills/CLAUDE.md) · curated workflow (planned): [docs/curated-skill-selection.md](docs/curated-skill-selection.md)

## Usage

Skills are Markdown files (`SKILL.md`) in skill-specific directories under [`skills/`](skills/). Each skill has `name` and `description` in YAML frontmatter; IDEs discover skills when that tree is linked or installed.

**Format and CI:** Metadata must follow the [Agent Skills specification](https://agentskills.io/specification). Pull requests that touch `skills/` run `skills-ref` (pinned) and a non-interactive [Skills CLI](https://github.com/vercel-labs/skills) discovery smoke (`npx skills add … --list`). Tooling rationale: [ADR 001 — Skill validation and tooling](docs/decisions/001-skill-validation-and-tooling.md).

## IDE setup

Reference the **`skills/`** folder from your IDE. Do not duplicate skills. Symlinks below work for **Cursor**, **Claude**, and **Codex**.

### Option A: Symlinks (recommended)

Symlink targets must be the **inner** Agent Skills tree in this repository: the directory named `skills/` at the **root of the `pkuppens/skills` clone** (same level as this `README.md`). That inner folder will contain `SKILL_TREE.md`, `CLAUDE.md`, and per-skill folders after migration.

**Project-level** (your app repo sits beside the `pkuppens/skills` clone):

```bash
# Layout example:
#   repos/
#     my-app/
#     pkuppens-skills/    # clone of github.com/pkuppens/skills
mkdir -p .cursor
ln -s ../pkuppens-skills/skills .cursor/skills
# or
mkdir -p .claude
ln -s ../pkuppens-skills/skills .claude/skills
```

Adjust the relative path to match your clone location and folder name.

**User-level (all projects):**

```bash
mkdir -p ~/.cursor ~/.claude ~/.codex
ln -s /path/to/pkuppens-skills-clone/skills ~/.cursor/skills
ln -s /path/to/pkuppens-skills-clone/skills ~/.claude/skills
ln -s /path/to/pkuppens-skills-clone/skills ~/.codex/skills
```

**Windows:** Symlinks may require Administrator rights or Developer Mode. Alternative: `mklink /D .cursor\skills <path-to-skills-folder>` (cmd as Admin).

### Option B: Sync script

Add `scripts/sync-skills-to-ide.sh` in your environment to copy or symlink `skills/` into `~/.cursor/skills/pkuppens`, `~/.claude/skills/pkuppens`, etc.

### IDE expected locations

| IDE | Project | User |
|-----|---------|------|
| Cursor | `.cursor/skills/`, `.agents/skills/` | `~/.cursor/skills/` |
| Claude | `.claude/skills/` | `~/.claude/skills/` |
| Codex | — | `~/.codex/skills/` |

Cursor also loads from `.claude/skills/` and `~/.claude/skills/`.

## Install this library with the Skills CLI (`npx skills`)

**Goal:** Install skills from **this** repository the same way as packages from [skills.sh](https://www.skills.sh/) and the [Skills CLI](https://github.com/vercel-labs/skills)—the CLI clones from Git and discovers `SKILL.md` under [`skills/`](https://github.com/vercel-labs/skills#readme).

**Who it is for:** Anyone who prefers the installer over manual symlinks ([Option A](#option-a-symlinks-recommended)), or who wants a **subset** with `--skill`.

**Layout contract:** Each skill is `skills/<directory>/SKILL.md`; YAML `name` must match `<directory>` ([Agent Skills](https://agentskills.io/specification), `skills-ref`).

**Commands** (pin `skills@…` to match [.github/workflows/validate-skills.yml](.github/workflows/validate-skills.yml); examples use **1.5.6**):

```bash
# List skills the CLI would install from this repo (non-interactive)
npx --yes skills@1.5.6 add https://github.com/pkuppens/skills --list -y

# Install one skill by YAML name (project scope; add -g for user-wide)
npx --yes skills@1.5.6 add pkuppens/skills --skill plan -y

# Target specific agents (repeat -a as needed)
npx --yes skills@1.5.6 add pkuppens/skills --skill plan -y -a cursor -a claude-code

# Install many by name
npx --yes skills@1.5.6 add pkuppens/skills --skill plan --skill test -y
```

Use `npx skills add --help` for current flags. Installs default to **symlinks**; use `--copy` when symlinks are unsupported.

**Verify an install:**

1. `npx skills list` (or `npx skills ls`) for the scope you used (`-g` vs project).
2. Confirm files under paths from [IDE expected locations](#ide-expected-locations).
3. Run `skills-ref validate <path-to-skill-dir>` to mirror CI ([skills-ref](https://www.npmjs.com/package/skills-ref)).

### Pinning / versions (reproducibility)

CLI installs are **Git-based**. The [Skills CLI](https://github.com/vercel-labs/skills) accepts `@<ref>` on `owner/repo`:

| Install style | Example | When to use |
|---------------|---------|-------------|
| Floating (default branch) | `pkuppens/skills` or `https://github.com/pkuppens/skills` | Latest `main`; behaviour may change. |
| Pinned to commit | `pkuppens/skills@<commit-sha>` | Reproducible CI or team baseline. |
| Pinned to tag | `pkuppens/skills@<tag>` | Stable human-readable ref after tags exist. |
| Pinned to branch | `pkuppens/skills@my-branch` | Long-lived branch installs. |

```bash
npx --yes skills@1.5.6 add pkuppens/skills@<git-ref> --list -y
```

Record `owner/repo@ref` in project docs (`CLAUDE.md`, `docs/skills-used.md`, etc.). After publishing migration tags, prefer pinning tags for baselines (see release notes in GitHub issues).

Optional `metadata.version` on a skill does **not** control what the CLI clones—**`@ref` does**.

## External and vendor skills

Symlinks here target **this** repo’s `skills/` tree. Extra packages from the ecosystem (`npx skills add …`) live beside it under IDE paths and are **not** committed here.

**Where to record extras:** `CLAUDE.md`, `CONTRIBUTING.md`, or `docs/skills-used.md` (source URL, command, owner, last reviewed).

**Example:**

```bash
npx skills add https://github.com/github/awesome-copilot --skill azure-devops-cli
```

Authoring guidance (“install first; author only when needed”) will live in [`skills/_meta/skill-creation/reference.md`](skills/_meta/skill-creation/reference.md) once migrated.

## Canonical plus public skills (side by side)

**Merge model:** One discovery surface from **(A)** this repo’s `skills/` tree and **(B)** CLI-installed packages. They coexist under `.cursor/skills/`, `~/.cursor/skills/`, etc.

- Order of install vs symlink does not matter for discovery; refresh the IDE if paths are cached.
- **Avoid duplicate ownership** if a public skill already covers a topic; document deltas if you fork.
- **Name collisions:** duplicate YAML `names` confuse discovery—prefer one copy or rename with rationale.

### Layout tip: child folder for this repo

If the CLI must own the skill root, symlink **one child** (e.g. `.cursor/skills/pkuppens` → `…/pkuppens/skills/skills`) and let other installs sit as siblings.

## Documentation layout

```text
pkuppens/skills/
├── README.md                 # This file (GitHub landing)
├── docs/
│   ├── decisions/
│   │   └── 001-skill-validation-and-tooling.md
│   ├── curated-skill-selection.md   # planned (#90)
│   └── bundles/                   # planned (#90)
├── skills/
│   ├── README.md             # Pointer / conventions (see migration issues)
│   ├── repo-bootstrap/       # temporary SKILL.md until migration replaces it
│   ├── SKILL_TREE.md         # after migration
│   ├── CLAUDE.md
│   └── …                     # skill directories
└── .github/workflows/
    └── validate-skills.yml
```

## Migration note

Content is moving from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) per [issue #90](https://github.com/pkuppens/pkuppens/issues/90). Track progress via issues in **this** repository.
