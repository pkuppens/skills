# Unified AI coding skills

Canonical **Agent Skills** library for Cursor, Claude, and Codex. The skills span shell and terminal work, README and documentation authoring, architecture and CTO-level strategy, code review, and ML/CV guidance — plus meta tooling for transferring and validating skills. See [What's inside](#whats-inside) for the map and [skills/SKILL_TREE.md](skills/SKILL_TREE.md) for the full index. GitHub profile narrative stays in [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens); **this repository is the skills-only home.**

**Quick links:** [skills/SKILL_TREE.md](skills/SKILL_TREE.md) (full index) · [skills/COOPERATION.md](skills/COOPERATION.md) (how skills compose) · [skills/CLAUDE.md](skills/CLAUDE.md) (agent rules)

## Quick start: install one skill and use it

**This is the main audience.** You want to use a skill in your own workflow — not clone this repo or work on the skills. Install one skill from GitHub with the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
# Add the readme-authoring skill to the current project for Claude Code
npx --yes skills add pkuppens/skills --skill readme-authoring -y -a claude-code
```

It lands under `.claude/skills/readme-authoring/`. Use `-g` for a user-wide install, or another `-a` target (`cursor`, `codex`). See [IDE expected locations](#ide-expected-locations).

**Use it in Claude.** Claude loads the skill by its description when you ask for README work. Or invoke it directly:

```text
/readme-authoring review this repo's README
```

Swap `readme-authoring` for any skill in [What's inside](#whats-inside) — for example `--skill terminal` for shell guidance.

> [!TIP]
> Prefer symlinks, or want the whole library at once? See [IDE setup](#ide-setup) and [Install this library with the Skills CLI](#install-this-library-with-the-skills-cli-npx-skills).

### Claude Code: install natively via plugin marketplace

This repo is also a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) (`.claude-plugin/marketplace.json`) — one plugin per skill, no Skills CLI or Node.js required:

```text
/plugin marketplace add pkuppens/skills
/plugin install branch-cleanup@pkuppens-skills
```

Swap `branch-cleanup` for any skill name in [What's inside](#whats-inside). `/plugin list` shows what's installed; `/plugin uninstall <name>@pkuppens-skills` removes it.

## What's inside

Every skill is one `skills/<name>/SKILL.md`. Categories below mirror [SKILL_TREE.md](skills/SKILL_TREE.md), where each skill has a full description.

| Category | Skills |
| --- | --- |
| **Shell / terminal** ([index](skills/SKILL_TREE.md#language-and-framework-skills)) | `terminal` orchestrator routing to `cmd`, `powershell`, `bash`, and `zsh` leaves |
| **Documentation** ([index](skills/SKILL_TREE.md#documentation-skills)) | `readme-authoring` |
| **Strategy, review & ML/CV** ([index](skills/SKILL_TREE.md#strategy-and-lifecycle-skills)) | `tech-stack-recommender`, `architecture-pattern-selector`, `scalability-advisor`, `cost-estimator`, `roadmap-generator`, `delegation-prompt-crafter`, `request-analyzer`, `clarification-protocol`, `antipattern-detector`, `assumption-challenger`, `brutally-honest-code-review`, `validation-report-generator`, `ml-cv-specialist` |
| **Repo maintenance** ([index](skills/SKILL_TREE.md#repo-maintenance)) | `branch-cleanup`, `dependabot` |
| **Agent orchestration** ([index](skills/SKILL_TREE.md#agent-orchestration)) | `ai-factory` |
| **Legacy refactoring** ([index](skills/SKILL_TREE.md#legacy-refactoring-skills)) | `oracle-first-refactor`, `call-site-exhaustiveness`, `legacy-build-container` |
| **Meta** ([index](skills/SKILL_TREE.md#meta)) | `skills-transfer`, `repo-transfer` (install, catalog, and land skills via PR), `skill-creation` (author new skills) |

> [!TIP]
> The legacy-refactoring skills have a worked example with stored output: [`workshops/legacy-refactor/`](workshops/legacy-refactor/README.md) — refactoring a code base larger than any context window, on a public healthcare C#/C++ specimen.
>
> New to test-driven development? [`workshops/test-driven-development/`](workshops/test-driven-development/README.md) shows red, green, refactor step by step on the Bowling Game Kata, in Python.

## Getting the code

You only need a local clone to **contribute**, symlink the whole tree into an IDE, or browse offline — most users can stop at [Quick start](#quick-start-install-one-skill-and-use-it) above.

```bash
git clone https://github.com/pkuppens/skills.git
```

No forking, SSO, submodules, or LFS are required — a direct clone is enough for symlinking the tree or contributing. (Installing individual skills via the CLI needs no clone at all — see [Quick start](#quick-start-install-one-skill-and-use-it).)

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

Symlink targets must be the **inner** Agent Skills tree in this repository: the directory named `skills/` at the **root of the `pkuppens/skills` clone** (same level as this `README.md`). That inner folder contains `SKILL_TREE.md`, `CLAUDE.md`, `COOPERATION.md`, `_meta/`, and the per-skill folders.

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

## Pinning a version

Every install path clones from Git, so a fixed baseline is a **Git ref**: a release tag such as `v1.0.0` ([releases](https://github.com/pkuppens/skills/releases)), a commit SHA, or a branch. Pin in your project docs or CI when you need reproducible installs. npm versions of `skills` / `skills-ref` don't pin skill content.

Use **`#<ref>`**, which works for both the Skills CLI and the Claude Code marketplace:

| Install path | Pinned command | Notes |
|--------------|----------------|-------|
| **Skills CLI** | `npx --yes skills add pkuppens/skills#v1.0.0 --skill terminal -y` | Also `https://github.com/pkuppens/skills.git#v1.0.0`. **Not** `pkuppens/skills@v1.0.0`: the CLI ignores `@ref` and installs `main`. |
| **Claude Code marketplace** | `/plugin marketplace add pkuppens/skills#v1.0.0`, then `/plugin install terminal@pkuppens-skills` | The whole marketplace follows the ref; plugin versions shown are that commit's SHA. `/plugin marketplace update` stays on the pinned ref. |
| **Symlink / clone** | `git clone --branch v1.0.0 https://github.com/pkuppens/skills.git` | Or `git -C <clone> checkout v1.0.0` in an existing clone; symlinks then serve that version. |

Optional `metadata.version` in a skill's frontmatter does **not** control what gets cloned; the ref does.

## External and vendor skills

Symlinks here target **this** repo’s `skills/` tree. Extra packages from the ecosystem (`npx skills add …`) live beside it under IDE paths and are **not** committed here.

**Superseded vendor skills:** The external `batch-files` skill is replaced by **`terminal/cmd`** in this library ([Epic #10](https://github.com/pkuppens/skills/issues/10)). After installing `terminal`, remove `batch-files` from `.agents/skills/` or your Skills CLI install to avoid duplicate CMD guidance.

**Where to record extras:** `CLAUDE.md`, `CONTRIBUTING.md`, or `docs/skills-used.md` (source URL, command, owner, last reviewed).

**Example:**

```bash
npx --yes skills add https://github.com/github/awesome-copilot --skill azure-devops-cli -y
```

Authoring guidance (“install first; author only when needed”) lives in [skills/_meta/skill-creation/reference.md](skills/_meta/skill-creation/reference.md#public-agent-skills-ecosystem-before-authoring).

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
├── .claude-plugin/
│   └── marketplace.json      # Claude Code plugin marketplace (one plugin per skill)
├── docs/
│   ├── agents/               # issue tracker, triage labels, domain-doc rules for agents
│   └── decisions/
│       ├── 001-skill-validation-and-tooling.md
│       ├── 002-workshop-container-environment.md
│       ├── 003-ai-assistance-network-and-confidentiality.md
│       └── 004-licensing-split.md
├── CONTEXT.md                # Domain glossary
├── LICENSE                   # MIT — covers skills/, tooling, docs outside workshops/
├── workshops/
│   ├── LICENSE               # CC BY-NC-ND 4.0 — covers workshops/ only
│   ├── legacy-refactor/      # worked example: notebooks with stored output
│   └── test-driven-development/  # TDD primer: Bowling Game Kata notebook
├── skills/
│   ├── README.md             # Pointer / conventions (see migration issues)
│   ├── skills-transfer/      # meta: install, sources, derivatives, catalog
│   │   └── repo-transfer/    # nested: land skills tree via PR
│   ├── SKILL_TREE.md         # skill index
│   ├── CLAUDE.md             # agent rules for skills/
│   ├── COOPERATION.md        # how skills compose
│   ├── _meta/                # skill-creation, human-ai-execution
│   └── …                     # skill directories
└── .github/workflows/
    └── validate-skills.yml
```

## Migration note

Content is moving from [`pkuppens/pkuppens`](https://github.com/pkuppens/pkuppens) per [issue #90](https://github.com/pkuppens/pkuppens/issues/90). Track progress via issues in **this** repository.

## Contributing

Report bugs or request skills via [GitHub issues](https://github.com/pkuppens/skills/issues). Pull requests that touch `skills/` must pass [`validate-skills.yml`](.github/workflows/validate-skills.yml) (`skills-ref validate` on every changed skill directory). See [ADR 001](docs/decisions/001-skill-validation-and-tooling.md) for the tooling rationale behind that check.

## Licence

This repository uses **two** licences. GitHub shows only the first one, so read this table before you reuse anything.

| What | Licence | What you may do |
| --- | --- | --- |
| `skills/`, repository tooling, and docs outside `workshops/` | [MIT](LICENSE) | Use, change, and build on it. Commercial use is allowed. |
| [`workshops/`](workshops/) — teaching material, notebooks, stored output | [CC BY-NC-ND 4.0](workshops/LICENSE) | Read it, keep it, and share it without change. No commercial use. No published changes. |
| Example code bases that a workshop clones (fo-dicom, DCMTK) | Their own licences | Not covered here. |

In short: **learn from the workshops, build with the skills.** To apply a method to your own code base, use the skills — they are MIT and meant to be adapted.

Reasons for the split: [ADR 004](docs/decisions/004-licensing-split.md).
