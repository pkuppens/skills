---
name: legacy-build-container
description: >
  Run from the root of any compiled project. Work out which toolchain the code
  needs, write a Docker build container and the instructions to use it, and
  record the result so the next attempt is faster. Use when a C++, C#, or other
  compiled project does not build with the current compiler, when a legacy
  build must be reproducible for an audit, or when an AI agent needs a working
  build as its oracle before it changes legacy code. When the evidence in the
  repository is not enough to choose a toolchain, report what is missing
  instead of guessing.
---

# Legacy build container

**Invoke:** `/legacy-build-container`, from the root of the project you must build.
**Use when:** an old code base does not build with the current toolchain, and
an agent or a team needs a working build.
**Status:** exercised by a real run from a foreign project root — a clone of
fo-dicom 4.0.8, in
[`workshops/legacy-refactor/evidence/legacy-build-container/`](../../workshops/legacy-refactor/evidence/legacy-build-container/README.md).
Two verified environments from executed runs: `gcc:4.9` pinned by digest for
C++03, and the .NET SDK for fo-dicom 4.0.8. Rows in
[`reference/verified-environments.md`](reference/verified-environments.md).
Guided tour of the method: [`00_setup.ipynb`](../../workshops/legacy-refactor/notebooks/00_setup.ipynb).
DCMTK at scale is not yet built.

**Why this matters:** the build is the first step of the
[test oracle](../../CONTEXT.md#language-legacy-refactoring) ladder. Without a build, nobody can prove that a change to
legacy code is complete. An agent without a build can only guess.

Environment decisions: [ADR 002](../../docs/decisions/002-workshop-container-environment.md).

---

## The contract

The skill takes one input: the directory you start it in. It needs no prior
knowledge of the project.

| | |
| --- | --- |
| **Input** | the project root. Nothing else is required. |
| **Output, success** | `build-container/Dockerfile`, `build-container/BUILD.md`, and a proposed row for [`reference/verified-environments.md`](reference/verified-environments.md). |
| **Output, not enough evidence** | the report in [When you cannot decide](#when-you-cannot-decide). Never a guessed Dockerfile. |
| **Needs** | a shell, `git`, and Docker. Network for the first image pull only. |
| **Writes** | files under `build-container/` only. The project belongs to somebody else. |

The skill runs ordinary shell commands: `git`, `docker`, and the project's own
build tool. It needs no MCP server and no special tool. An agent that has a
shell runs the procedure itself; a person with a terminal runs the same
commands by hand and gets the same result. Keep every command in `BUILD.md`
copy-pasteable for that reason.

## Rule 1 — Read the learned facts first

**Before you write a Dockerfile, read
[`reference/verified-environments.md`](reference/verified-environments.md).**

That file holds environments that built successfully, and traps that cost time.
A matching row saves one to three hours. Start from the row. Do not start from
an empty file.

## Rule 2 — Build in the container, not on the host

Do not install a toolchain on the host. A legacy project needs an old
compiler, and an old compiler on a working laptop is a cost that never ends.

A host build is allowed in one case only: the host already holds the toolchain,
and you want a smoke test of a few seconds before you spend minutes on an
image. Say which one you did. Never report a host build as the container build.

## Rule 3 — The agent runs where the toolchain runs

The agent must start the compiler. Therefore the agent runs inside the
container, or the agent runs the compiler through `docker exec`.

A common failure: the source is in the container, and the agent is on the host.
The agent then cannot see `cmake`, `clangd`, or `dotnet`. Check this first.

## Rule 4 — Mount the source. Do not copy it.

```bash
docker run --rm -it -v "$PWD:/work" -w /work <image> bash
```

The source stays on the host disk. This matters when the source is
confidential, because the image never holds it. See
[ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md).

## Rule 5 — Pin the base image by digest

A tag moves. A digest does not.

```dockerfile
FROM debian:bullseye@sha256:<digest>
```

Record the digest. Under IEC 62304 and similar rules, the digest is evidence of
a controlled build environment.

---

## Procedure

Follow these steps in order. Stop at the first failure and fix it.

### Step 1 — Confirm where you are, and that there is code to build

The code comes first. Tool needs are read out of the code, so there is nothing
to decide before the code is on disk.

```bash
git rev-parse --show-toplevel                 # you must be at a project root
git log -1 --date=short --format='%ad %h %s'  # how old is this code?
git describe --tags --always                  # which version is checked out?
```

If the directory is not a project root, stop. Ask for the root, or for the
clone command.

### Step 2 — Find the toolchain that the code needs

Read the build files, not the documentation. The build files are current.

```bash
git ls-files | grep -Ei '(CMakeLists\.txt|Makefile|configure\.ac|\.sln|\.csproj|\.vcxproj|packages\.config|\.pro|pom\.xml)$'
```

| Evidence | Where to look | What it tells you |
| --- | --- | --- |
| C++ standard | `CMakeLists.txt`, `configure.ac`, `*.vcxproj`, compiler flags | the lowest standard you must accept |
| Compiler age | `#if __GNUC__` guards, `#pragma` use, missing `nullptr` | which compiler generation the code expects |
| C# framework | `TargetFramework`, `TargetFrameworks`, `TargetFrameworkVersion`, `packages.config` | the SDK, and whether .NET Framework is involved |
| Build system | `CMakeLists.txt`, `Makefile`, `*.sln`, `autogen.sh` | which command builds it |
| Age of the code | the date of the oldest and the newest commit | a cross-check on everything above |

Write down the **oldest** requirement that you find, and the file that it came
from. That requirement sets the base image, and the file is the evidence for
it. A requirement with no file behind it is a guess.

### Step 3 — Choose the base image

| Need | Base image | Note |
| --- | --- | --- |
| GCC 4.x, C++98 or C++03 | **`gcc:4.9`** | **Preferred.** Verified: g++ 4.9.4 on Debian 8.9. The compiler is already in the image, so no package server is involved and the archived-mirror trap cannot happen. 1.3 GB. |
| GCC 4.x, if you need the distribution too | `debian:jessie` or `ubuntu:14.04` | Only when you must install more packages. The package servers moved; see the traps. |
| GCC 5 to 7, C++11 | `debian:stretch`, `ubuntu:16.04` | |
| GCC 8 to 10, C++14 or C++17 | `debian:bullseye` | |
| .NET Framework code on Linux | `mono:latest` | WinForms and WPF do not work. Libraries often do. |
| .NET Framework 4.x on Windows | A Windows container | Needed for WinForms and WPF. |
| .NET Core or .NET 5 and later | `mcr.microsoft.com/dotnet/sdk:<version>` | Match the `TargetFramework`. |

Prefer the newest image that still builds the code. An older image costs more
time. Record the digest, not the tag — Rule 5.

### Step 4 — Fix the package source before you install anything

This step prevents the most common failure. See the traps table. An image that
already holds the compiler needs no package server at all, which is why Step 3
prefers one.

### Step 5 — Write the two artifacts

Write both files under `build-container/`, and nothing anywhere else.

`build-container/Dockerfile` installs the compiler, the build system, and a
language server. The language server is oracle step 2.

```dockerfile
FROM <image>@sha256:<digest>
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake ninja-build clangd git \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
```

`build-container/BUILD.md` holds the commands a reader runs, and the facts a
reviewer checks: the image and its digest, how to build the image, how to start
the build, the smoke test, the build matrix, and whether a network is needed.
Use the [report format](reference/verified-environments.md#report-format).

### Step 6 — Build one subset target first

Do not build the whole project. Choose the smallest target that contains the
code that you must change.

```bash
docker build -t <project>-build build-container
docker run --rm -v "$PWD:/work" -w /work <project>-build \
  cmake -S . -B build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
docker run --rm -v "$PWD:/work" -w /work <project>-build \
  cmake --build build --target <subset>
```

`CMAKE_EXPORT_COMPILE_COMMANDS` writes `compile_commands.json`. The language
server needs that file. Without it, there is no semantic index.

### Step 7 — Declare the build matrix, even when it has one entry

The compiler is a sound oracle **only for the settings that you build**. So the
set of settings is part of the result, and it must be written down rather than
assumed.

Write the matrix as a list, even when the list has one entry:

```bash
# Build matrix. One entry on purpose: this run proves the method, not the full
# configuration space. Each extra entry multiplies build time, and every claim
# about complete recall is limited to the entries listed here.
MATRIX=("default")
# MATRIX=("default" "WITH_OPENSSL=ON" "WITH_ICU=ON")   # the real project's set
```

Two reasons to keep the single entry explicit instead of leaving it out:

1. The reader sees that a choice was made, not forgotten.
2. Adding the second entry later costs one line, so nobody has to restructure
   the script to widen the claim.

Report the entries that you built. Never report complete recall without them.

### Step 8 — Make the build work without a network

A demonstration or a CI job can have no network. Prepare for that state.

| Language | Action |
| --- | --- |
| C# | Vendor the packages into a local folder. Add a `nuget.config` with `<clear />` that points at that folder. Then use `dotnet build --no-restore`. |
| C++ | Prefer an image that already holds the compiler, such as `gcc:4.9`. Then `docker save -o image.tar` is the whole offline story. |
| C++ | Clone the dependencies into the image, or vendor them in the repository. |
| Any | Save the image with `docker save -o image.tar <image>`. Restore it with `docker load`. |

**Test this with the sources removed, not with the network merely idle.** Clear
the package sources and restore into an empty folder. Then run the same thing
with no local feed either: that negative control must fail. Without it, a pass
proves nothing — the restore could simply have reached the network.

### Step 9 — Record the result

Complete the step in [Rule 6](#rule-6-record-what-you-learned). Do not skip
it. The record is the value of this skill.

The traps below are also recorded in
[ADR 002](../../docs/decisions/002-workshop-container-environment.md), which
explains why this skill exists at all. Keep the two lists consistent.

---

## When you cannot decide

Some projects do not hold the evidence. A generated build system, a vendored
toolchain that is missing, or a build that only ever ran on one machine. Report
that state. Do not write a Dockerfile that you cannot defend.

```text
Project:        <path>, <version or commit>
Language:       <what the files say, or "cannot tell">
Build files:    <the files you found, or "none">
Blocked on:     <the one fact that is missing>
Evidence read:  <the files you actually opened>
Question:       <the single question whose answer unblocks this>
Best guess:     <an image, marked clearly as unverified, or "none">
```

Two rules for this report:

1. **Name one blocker, not a list.** A list reads as "this is hard". One
   blocker reads as "answer this and I continue".
2. **Mark a guess as a guess.** An unverified image in a report is useful. The
   same image in `verified-environments.md` is a defect.

---

## Rule 6: record what you learned

The skill improves because each run adds a fact. The record is a reviewed Git
commit, so the facts keep their provenance.

**After a green build**, append one row to
[`reference/verified-environments.md`](reference/verified-environments.md).
Then open a pull request.

**After a failure that cost more than 15 minutes**, append one line to the
traps list in the same file.

The limits on that file — green build only, one row per environment, at most
20 rows, one line per trap, a human merges it — are stated once, in
[its own rules](reference/verified-environments.md#rules-for-this-file). Read
them there before you append. The shape of a finished row is the
[report format](reference/verified-environments.md#report-format).

A false row is worse than no row. And an artifact that rewrites itself with no
review has no change control: in a regulated process that is a defect, not a
feature. The reviewable form is the compliant form.

## Traps

| Symptom | Cause | Fix |
| --- | --- | --- |
| `apt-get update` fails with 404 on an old image | The distribution moved to an archive server. | Point `apt` at `old-releases.ubuntu.com` or `archive.debian.org`. |
| The agent cannot find `cmake` | The agent runs on the host, and the toolchain is in the container. | Run the agent in the container, or use `docker exec`. |
| The build is very slow on Windows | The source is on a mounted Windows path. | Keep the source in the Linux file system, or accept the cost and build a smaller subset. |
| The language server reports no symbols | `compile_commands.json` is missing. | Add `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`. |
| `dotnet build` tries to reach the network | `restore` runs as part of `build`. | Vendor the packages and use `--no-restore`. |
| A WinForms or WPF project fails under Mono | Mono does not implement them. | Build the library projects only, or use a Windows container. |
| The image does not fit on the target disk | One image holds two toolchains. | Split the image per language. |

## Related skills

| Skill | Relation |
| --- | --- |
| [`call-site-exhaustiveness`](../call-site-exhaustiveness/SKILL.md) | Uses the build that this skill produces, to find every call site. |
| [`oracle-first-refactor`](../oracle-first-refactor/SKILL.md) | The build is oracle step 1 in its ladder. |
| [`ai-factory`](../ai-factory/SKILL.md) | Decides whether the model that uses this build runs locally or in the cloud. |
| [`terminal`](../terminal/SKILL.md) | Shell differences between the host and the container. |
