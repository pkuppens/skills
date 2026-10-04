---
name: legacy-build-container
description: >
  Build a Docker container that compiles an old code base with a
  period-correct toolchain, then record the result so the next attempt is
  faster. Use when a C++, C#, or other compiled project does not build with
  the current compiler, when a legacy build must be reproducible for an audit,
  or when an AI agent needs a working build as its oracle before it changes
  legacy code.
---

# Legacy build container

**Invoke:** `/legacy-build-container`
**Use when:** an old code base does not build with the current toolchain, and
an agent or a team needs a working build.
**Status:** two verified environments, both from executed runs: `gcc:4.9`
pinned by digest for C++03, and the host .NET SDK for fo-dicom 4.0.8. Rows in
[`reference/verified-environments.md`](reference/verified-environments.md).
Evidence: [`00_setup.ipynb`](../../workshops/legacy-refactor/notebooks/00_setup.ipynb).
DCMTK at scale is not yet built.

**Why this matters:** the build is the first rung of the
[test oracle](../../CONTEXT.md#language-legacy-refactoring) ladder. Without a build, nobody can prove that a change to
legacy code is complete. An agent without a build can only guess.

Environment decisions: [ADR 002](../../docs/decisions/002-workshop-container-environment.md).

---

## Rule 1 — Read the learned facts first

**Before you write a Dockerfile, read
[`reference/verified-environments.md`](reference/verified-environments.md).**

That file holds environments that built successfully, and traps that cost time.
A matching row saves one to three hours. Start from the row. Do not start from
an empty file.

## Rule 2 — The agent runs where the toolchain runs

The agent must start the compiler. Therefore the agent runs inside the
container, or the agent runs the compiler through `docker exec`.

A common failure: the source is in the container, and the agent is on the host.
The agent then cannot see `cmake`, `clangd`, or `dotnet`. Check this first.

## Rule 3 — Mount the source. Do not copy it.

```bash
docker run --rm -it -v "$PWD:/work" -w /work <image> bash
```

The source stays on the host disk. This matters when the source is
confidential, because the image never holds it. See
[ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md).

## Rule 4 — Pin the base image by digest

A tag moves. A digest does not.

```dockerfile
FROM debian:bullseye@sha256:<digest>
```

Record the digest. Under IEC 62304 and similar rules, the digest is evidence of
a controlled build environment.

---

## Procedure

Follow these steps in order. Stop at the first failure and fix it.

### Step 1 — Find the toolchain that the code needs

Read the build files, not the documentation. The build files are current.

| Evidence | Where to look |
| --- | --- |
| C++ standard | `CMakeLists.txt`, `configure.ac`, `*.vcxproj`, compiler flags |
| Compiler age | `#if __GNUC__` guards, `#pragma` use, missing `nullptr` |
| C# framework | `TargetFramework`, `TargetFrameworkVersion`, `packages.config` |
| Build system | `CMakeLists.txt`, `Makefile`, `*.sln`, `autogen.sh` |

Write down the oldest requirement that you find. That requirement sets the base
image.

### Step 2 — Choose the base image

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
time.

### Step 3 — Fix the package source before you install anything

This step prevents the most common failure. See the traps table.

### Step 4 — Install the toolchain and the index

Install the compiler, the build system, and a language server. The language
server is step 2 of the oracle ladder.

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake ninja-build clangd git \
 && rm -rf /var/lib/apt/lists/*
```

### Step 5 — Build one subset target first

Do not build the whole project. Choose the smallest target that contains the
code that you must change.

```bash
cmake -S . -B build -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --target <subset>
```

`CMAKE_EXPORT_COMPILE_COMMANDS` writes `compile_commands.json`. The language
server needs that file. Without it, there is no semantic index.

### Step 6 — Declare the build matrix, even when it has one entry

The compiler is a sound oracle **only for the settings that you build**. So the
set of settings is part of the result, and it must be written down rather than
assumed.

Write the matrix as a list, in the build script or the notebook, even when the
list has one entry:

```bash
# Build matrix. One entry on purpose: the workshop proves the method, not the
# full configuration space. Each extra entry multiplies build time, and every
# claim about complete recall is limited to the entries listed here.
MATRIX=("default")
# MATRIX=("default" "WITH_OPENSSL=ON" "WITH_ICU=ON")   # the real project's set
```

Two reasons to keep the single entry explicit instead of leaving it out:

1. The reader sees that a choice was made, not forgotten.
2. Adding the second entry later costs one line, so nobody has to restructure
   the script to widen the claim.

Report the entries that you built. Never report complete recall without them.

### Step 7 — Make the build work without a network

A demonstration or a CI job can have no network. Prepare for that state.

| Language | Action |
| --- | --- |
| C# | Vendor the packages into a local folder. Add a `nuget.config` that points at that folder. Then use `dotnet build --no-restore`. |
| C++ | Prefer an image that already holds the compiler, such as `gcc:4.9`. Then `docker save -o image.tar` is the whole offline story. |
| C++ | Clone the dependencies into the image, or vendor them in the repository. |
| Any | Save the image with `docker save -o image.tar <image>`. Restore it with `docker load`. |

**Test this with the network switched off.** A network that is merely idle is
not a test.

### Step 8 — Record the result

Complete the step in [Rule 5](#rule-5-record-what-you-learned). Do not skip
it. The record is the value of this skill.

The traps below are also recorded in
[ADR 002](../../docs/decisions/002-workshop-container-environment.md), which
explains why this skill exists at all. Keep the two lists consistent.

---

## Rule 5: record what you learned

The skill improves because each run adds a fact. The record is a reviewed Git
commit, so the facts keep their provenance.

**After a green build**, append one row to
[`reference/verified-environments.md`](reference/verified-environments.md).
Then open a pull request.

**After a failure that cost more than 15 minutes**, append one line to the
traps list in the same file.

Obey these limits:

1. **Append a verified row only after a green build.** Never record an
   environment that you did not build. A false row is worse than no row.
2. **One row per environment.** Update an existing row; do not add a duplicate.
3. **Keep the file short.** Hold at most 20 verified rows, newest first. Remove
   the oldest row when the file is full. A long file wastes the context of
   every later run.
4. **A trap is one line.** Name the symptom and the fix. Do not write a report.
5. **A human merges the change.** This skill proposes. It does not self-approve.

An artifact that rewrites itself with no review has no change control. In a
regulated process that is a defect, not a feature. The reviewable form is the
compliant form.

---

## Report format

Report the environment like this. A reader must be able to repeat it.

```text
Base image:   debian:bullseye@sha256:abc123...
Compiler:     g++ (Debian 10.2.1-6) 10.2.1
Build system: cmake 3.18.4, ninja 1.10.1
Index:        clangd 11, compile_commands.json present
Target built: ofstd, dcmdata
Build time:   4 min 12 s, 4 cores
Network:      not needed after the image exists
```

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
| [`oracle-first-refactor`](../oracle-first-refactor/SKILL.md) | The build is oracle 1 in its ladder. |
| [`ai-factory`](../ai-factory/SKILL.md) | Decides whether the model that uses this build runs locally or in the cloud. |
| [`terminal`](../terminal/SKILL.md) | Shell differences between the host and the container. |
