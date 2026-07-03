# Unified AI coding skills

Canonical **Agent Skills** library for Cursor, Claude, and Codex: arc42-aligned workflows from ideation through operations. GitHub profile narrative stays in [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens); **this repository is the skills-only home.**

**Quick links:** [skills/SKILL_TREE.md](skills/SKILL_TREE.md) (full index) · `skills/COOPERATION.md`, `skills/CLAUDE.md` (planned, [#5](https://github.com/pkuppens/skills/issues/5)) · curated workflow (planned, [#7](https://github.com/pkuppens/skills/issues/7)): `docs/curated-skill-selection.md`

## Getting the code

```bash
git clone https://github.com/pkuppens/skills.git
```

No forking, SSO, submodules, or LFS are required — a direct clone is enough for symlinking, CLI install, or contributing.

## Prerequisites

| Tool | Version | Why |
| --- | --- | --- |
| [Git](https://git-scm.com/) | any recent | clone the repo and symlink or install skills |
| [Node.js](https://nodejs.org/) | 24.x (matches [`validate-skills.yml`](.github/workflows/validate-skills.yml)) | run `npx skills` (Skills CLI) and `skills-ref validate` locally, the same checks CI runs on pull requests |

This repo does not pin a Node version via `.nvmrc`/`volta`/`engines` — match CI's Node 24 if you want local `skills-ref validate` runs to behave the same as the pipeline.

Verify your setup:

```bash
git --version
node --version
```

## Usage

Skills are Markdown files (`SKILL.md`) in skill-specific directories under [`skills/`](skills/). Each skill has `name` and `description` in YAML frontmatter; IDEs discover skills when that tree is linked or installed.

**Format and CI:** Metadata must follow the [Agent Skills specification](https://agentskills.io/specification). Pull requests that touch `skills/` run latest `skills-ref` and a non-interactive [Skills CLI](https://github.com/vercel-labs/skills) discovery smoke (`npx skills add … --list`). Tooling rationale: [ADR 001 — Skill validation and tooling](docs/decisions/001-skill-validation-and-tooling.md). **Transfer/install:** skill [`skills-transfer`](skills/skills-transfer/SKILL.md).

## IDE setup

Reference the **`skills/`** folder from your IDE. Do not duplicate skills. Symlinks below work for **Cursor**, **Claude**, and **Codex**.

### Option A: Symlinks (recommended)

Symlink targets must be the **inner** Agent Skills tree in this repository: the directory named `skills/` at the **root of the `pkuppens/skills` clone** (same level as this `README.md`). That inner folder already contains `SKILL_TREE.md` and per-skill folders; `CLAUDE.md` lands with migration ([#5](https://github.com/pkuppens/skills/issues/5)).

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

**Commands** (floating `npx skills` — same as CI; this library does not pin npm tool versions):

```bash
# List skills the CLI would install from this repo (non-interactive)
npx --yes skills add https://github.com/pkuppens/skills --list -y

# Install one skill by YAML name (project scope; add -g for user-wide)
npx --yes skills add pkuppens/skills --skill skills-transfer -y

# Target specific agents (repeat -a as needed)
npx --yes skills add pkuppens/skills --skill skills-transfer -y -a cursor -a claude-code

# Install terminal skill from this repository
npx --yes skills add pkuppens/skills --skill terminal -y
```

Use `npx skills add --help` for current flags. Installs default to **symlinks**; use `--copy` when symlinks are unsupported. Full transfer guidance: [`skills/skills-transfer/SKILL.md`](skills/skills-transfer/SKILL.md).

**Verify an install:**

1. `npx skills list` (or `npx skills ls`) for the scope you used (`-g` vs project).
2. Confirm files under paths from [IDE expected locations](#ide-expected-locations).
3. Run `skills-ref validate <path-to-skill-dir>` to mirror CI ([skills-ref](https://www.npmjs.com/package/skills-ref)).

### Git refs on installs (reproducibility)

CLI installs are **Git-based**. Pin **`owner/repo@<ref>`** in consumer project docs when you need a fixed baseline—not npm versions of `skills` or `skills-ref`:

| Install style | Example | When to use |
|---------------|---------|-------------|
| Floating (default branch) | `pkuppens/skills` | Latest `main` |
| Pinned to commit / tag / branch | `pkuppens/skills@<ref>` | Team or CI baseline |

```bash
npx --yes skills add pkuppens/skills@<git-ref> --list -y
```

Optional `metadata.version` on a skill does **not** control what the CLI clones—**`@ref` does**.

## External and vendor skills

Symlinks here target **this** repo’s `skills/` tree. Extra packages from the ecosystem (`npx skills add …`) live beside it under IDE paths and are **not** committed here.

**Superseded vendor skills:** The external `batch-files` skill is replaced by **`terminal/cmd`** in this library ([Epic #10](https://github.com/pkuppens/skills/issues/10)). After installing `terminal`, remove `batch-files` from `.agents/skills/` or your Skills CLI install to avoid duplicate CMD guidance.

**Where to record extras:** `CLAUDE.md`, `CONTRIBUTING.md`, or `docs/skills-used.md` (source URL, command, owner, last reviewed).

**Example:**

```bash
npx --yes skills add https://github.com/github/awesome-copilot --skill azure-devops-cli -y
```

Authoring guidance (“install first; author only when needed”) will live in `skills/_meta/skill-creation/reference.md` once migrated (planned, [#5](https://github.com/pkuppens/skills/issues/5)).

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
│   ├── curated-skill-selection.md   # planned (#7)
│   └── bundles/                   # planned (#7)
├── CONTEXT.md                # Domain glossary
├── skills/
│   ├── README.md             # Pointer / conventions (see migration issues)
│   ├── skills-transfer/      # meta: install, sources, derivatives, catalog
│   │   └── repo-transfer/    # nested: land skills tree via PR
│   ├── SKILL_TREE.md         # skill index
│   ├── CLAUDE.md             # planned (#5)
│   └── …                     # skill directories
└── .github/workflows/
    └── validate-skills.yml
```

## Migration note

Content is moving from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) per [issue #90](https://github.com/pkuppens/pkuppens/issues/90). Track progress via issues in **this** repository.

## Contributing

Report bugs or request skills via [GitHub issues](https://github.com/pkuppens/skills/issues). Pull requests that touch `skills/` must pass [`validate-skills.yml`](.github/workflows/validate-skills.yml) (`skills-ref validate` on every changed skill directory). See [ADR 001](docs/decisions/001-skill-validation-and-tooling.md) for the tooling rationale behind that check.

Licensed under the [MIT License](LICENSE).
