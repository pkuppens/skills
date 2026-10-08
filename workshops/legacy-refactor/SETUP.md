# Setup

There are three ways to take part. Pick the first one that is enough for you.

| Level | What you can do | What you need |
| --- | --- | --- |
| A. Read | Follow the session. Read every notebook with its results. | A web browser. Nothing to install. |
| B. Use the skills | Run the method on your own code base. | Claude Code (or another agent), and optionally Node.js. |
| C. Run the notebooks | Repeat the workshop runs on your own machine. | Git, Docker, the .NET SDK, ripgrep, and Python with Jupyter. |

## A. Read

Open the [workshop README](README.md) on GitHub and click a notebook. GitHub
shows the stored results of each cell. That is all you need for the session.

## B. Use the skills on your own code

The workshop uses three skills:

- `legacy-build-container`
- `call-site-exhaustiveness`
- `oracle-first-refactor`

Install them in the root of **your own** project. Choose one of two ways.

**Option 1: Claude Code plugin. No Node.js needed.** Type this inside Claude
Code:

```text
/plugin marketplace add pkuppens/skills
/plugin install legacy-build-container@pkuppens-skills
/plugin install call-site-exhaustiveness@pkuppens-skills
/plugin install oracle-first-refactor@pkuppens-skills
```

**Option 2: Skills CLI. Needs [Node.js](https://nodejs.org/) 24.** Works for
Claude Code, Cursor and Codex. Run this in a terminal, in your project root:

```bash
npx --yes skills add pkuppens/skills \
  --skill legacy-build-container \
  --skill call-site-exhaustiveness \
  --skill oracle-first-refactor \
  -y -a claude-code
```

The skills land in `.claude/skills/`. Use `-a cursor` or `-a codex` for other
agents, and `-g` to install for your user instead of one project.

**Check:** `.claude/skills/` now holds three folders, each with a `SKILL.md`.
Then start Claude Code in your project and type `/legacy-build-container`.

The skills themselves call ordinary tools (Git, Docker, your compiler). Install
those as for level C.

## C. Run the notebooks yourself

### 1. Install the tools

| Tool | Why | Check |
| --- | --- | --- |
| [Git](https://git-scm.com/) | Clone this repository and the example code. | `git --version` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | The build runs in a container. Start it before you run a notebook. | `docker version` |
| [.NET SDK](https://dotnet.microsoft.com/download) 8 or newer | Build the C# example code. | `dotnet --version` |
| [ripgrep](https://github.com/BurntSushi/ripgrep) | The text search in `01a`. | `rg --version` |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Installs the pinned Python and packages. You do not need your own Python. | `uv --version` |

### 2. Get the code and a Python environment

```bash
git clone https://github.com/pkuppens/skills.git
cd skills/workshops/legacy-refactor
uv sync
```

`uv sync` reads `.python-version` (3.12), `pyproject.toml` and `uv.lock`, and
creates `.venv/` with exactly those versions. Everyone gets the same
environment, and you do not activate anything: `uv run` uses it.

**Check:** `uv run jupyter nbconvert --version` prints a version number.

### 3. Run the notebooks, in this order

`00_setup` downloads the example code (fo-dicom 4.0.8) and builds the
container. The other notebooks need that, so run it first. The first run needs
a network and takes several minutes.

Write the results to a new file, so the stored results in Git stay as they are:

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/00_setup.ipynb --output my_00_setup.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/01_build_warnings.ipynb --output my_01_build_warnings.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/01a_find_obsolete_call_sites.ipynb --output my_01a.ipynb
```

Everything the notebooks download goes into `tmp/workshop-workspace/` at the
repository root. That folder is ignored by Git. Delete it to start clean.

Start Docker Desktop first. The known pitfalls, with their fixes, are in the
*Run this notebook yourself* cell at the top of `00_setup`.

**Check:** compare your `my_*.ipynb` with the stored notebook. The counts must
match: the fo-dicom Core build shows 11 warnings in `00` and `01`, and `01a`
finds 62 text matches against 6 compiler uses.

## What was tested

Tested on Windows 11, 2026-10-06:

- Option 2 (Skills CLI) installed all three skills into an empty project.
- `uv sync` in step C.2 created the environment, and `jupyter nbconvert` ran.

- `00_setup` ran from scratch with `uv run`: no workspace and no images
  beforehand, Docker Desktop started. All cells passed in about 4 minutes, and
  every checked number matched the earlier run on another machine.

Not yet tested from a clean machine: option 1 (plugin) for these three skills,
and a from-scratch run of `01` and `01a`. That check is still open.
