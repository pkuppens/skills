# Verified environments

Facts that came from real runs. This file is the memory of the
[`legacy-build-container`](../SKILL.md) skill.

**Read this file before you write a Dockerfile.** A matching row saves one to
three hours.

## Rules for this file

1. Append a verified row **only after a green build**. Never record an
   environment that you did not build.
2. One row per environment. Update a row; do not duplicate it.
3. Hold at most 20 verified rows. Newest first. Remove the oldest row when the
   file is full.
4. A trap is one line: the symptom and the fix.
5. A human merges the change. This file is updated by a pull request, never by
   a direct write to the default branch.

A false row is worse than no row. In a regulated process this file can become
evidence.

## Report format

Report a finished environment like this, in `build-container/BUILD.md` and in
the pull request. A reader must be able to repeat it.

```text
Base image:   debian:bullseye@sha256:abc123...
Compiler:     g++ (Debian 10.2.1-6) 10.2.1
Build system: cmake 3.18.4, ninja 1.10.1
Index:        clangd 11, compile_commands.json present
Target built: ofstd, dcmdata
Build matrix: ["default"]
Build time:   4 min 12 s, 4 cores
Network:      not needed after the image exists
```

A field you did not measure says `not measured`. It never says a plausible
value.

## Verified rows

### fo-dicom 4.0.8 — .NET SDK 8.0 in a container — 2026-10-05

| Field | Value |
| --- | --- |
| Base image | `mcr.microsoft.com/dotnet/sdk:8.0@sha256:78235e09001f52b6592c458ac010775ebac6725422e80cd0c1650590f67b2743` |
| Image size | 867 MB |
| Compiler | .NET SDK `8.0.425`, Roslyn, C# 8 |
| Build system | `dotnet build`, from the SDK image. No `apt-get`, so no package server. |
| Target | `FO-DICOM.Core`, `netstandard2.0`, `fo-dicom.core.dll`, 1540096 bytes |
| Build matrix | `["FO-DICOM.Core/netstandard2.0"]` — one entry, declared |
| Build time | image 0.9 s; restore 5.7 s online, 5.3 s offline; build 7.1 s; 32 cores |
| Index | Roslyn, inside the SDK. No compilation database applies. |
| Package source | a vendored feed of 22 `.nupkg` files, 11 MB, with `<clear />` |
| Network needed after the image exists | **no, proved.** A cold cache plus `--network none` restores in 5.31 s and builds green. Negative control with no feed: exit 1, 6 × `NU1100`. |
| Result | Oracle step 1 available in a container. 0 errors, 11 warnings, 5 distinct codes. |
| Verified by | `/legacy-build-container`, started in the clone root with no other prompt. Record: [`evidence/legacy-build-container/`](../../../workshops/legacy-refactor/evidence/legacy-build-container/README.md) |

**Newest image that builds the target, not an old one.** `net462`,
`netcoreapp2.1`, `netcoreapp3.1`, the WinForms tools and the C++/CLI
`Native/Desktop` projects are out of the matrix: they need Windows or Mono, and
none of them is on the path to the core library.

**This row does not replace the host row below.** One records the host SDK, the
other a container. Both were measured.

### C++03 fixture — g++ 4.9 in a container — 2026-10-04

| Field | Value |
| --- | --- |
| Base image | `gcc:4.9@sha256:6356ef8b29cc3522527a85b6c58a28626744514bea87a10ff2bf67599a7474f5` |
| Image size | 1305 MB |
| Compiler | `g++ (GCC) 4.9.4`, Debian 8.9 (jessie), `GNU ld 2.25` |
| Build system | `g++` called directly. The fixture is two files, so no CMake. |
| Flags | `-std=c++03 -Werror=deprecated-declarations` |
| Index | none. No `compile_commands.json` for a two-file fixture. |
| Package source | **not used.** The image already holds the compiler. |
| Network needed after the image exists | no |
| Result | 5 deprecated call sites reported: 3 written by a macro, 1 direct, 1 from a template instantiation. A text search showed 1. |
| Verified by | [`00_setup.ipynb`](../../../workshops/legacy-refactor/notebooks/00_setup.ipynb), executed |

**Why this image and not an old distribution.** `gcc:4.9` carries a 2016
toolchain and needs no package server, so it avoids the archived-mirror trap
below entirely. Prefer an image that already holds the compiler over an old
base plus `apt`.

### fo-dicom 4.0.8 — .NET SDK on the host — 2026-10-04

| Field | Value |
| --- | --- |
| Base image | none. The host SDK builds it. |
| Compiler | .NET SDK `10.0.400` |
| Target | `FO-DICOM.Core`, `netstandard2.0`, C# 8 |
| Build system | `dotnet build` |
| Build matrix | `["FO-DICOM.Core/netstandard2.0"]` — one entry, declared |
| Rebuild time | 1.4 s, clean rebuild |
| Index | Roslyn. No compilation database needed. |
| Network needed after the first restore | **no, proved.** A local feed of 16 `.nupkg` files (9.4 MB) with `<clear />` in `nuget.config` restores into a cold package folder in under half a second and builds in about two seconds. Negative control with no feed: 6 × `NU1101`. |
| Result | Oracle step 1 available. 0 errors, 5 distinct warning kinds. |
| Verified by | [`00_setup.ipynb`](../../../workshops/legacy-refactor/notebooks/00_setup.ipynb) and [`05_refactoring.ipynb`](../../../workshops/legacy-refactor/notebooks/05_refactoring.ipynb), both executed |

**Note.** The clone declares eight target frameworks, including `net462` and
`netstandard1.3`. Only the one in the matrix was built, so any claim of
complete recall is limited to it.

<!--
Row template. Copy it, fill it, and put the newest row at the top.

### <code base> — <language> — <date>

| Field | Value |
| --- | --- |
| Base image | `<name>@sha256:<digest>` |
| Compiler | `<name and version>` |
| Build system | `<name and version>` |
| Index | `<language server>`, `compile_commands.json` present or not |
| Targets built | `<target list>` |
| Build time | `<time>`, `<cores>` cores |
| Package source | `<default>` or `<archive host>` |
| Network needed after build | yes or no |
| Verified by | `<who>`, `<commit>` |
-->

## Traps

One line for each failure that cost more than 15 minutes.

| Date | Symptom | Fix |
| --- | --- | --- |
| 2026-10-04 | `apt-get update` returns 404 on `ubuntu:14.04` and similar old images. | Point `apt` at `old-releases.ubuntu.com`. For old Debian, use `archive.debian.org`. |
| 2026-10-04 | `dotnet build` fails with no network, although the packages are present. | `build` runs `restore` first. Vendor the packages, add a local `nuget.config`, and use `dotnet build --no-restore`. |
| 2026-10-04 | The agent reports that `cmake` does not exist, and the build works in a terminal. | The agent runs on the host. The toolchain is in the container. Run the agent in the container, or use `docker exec`. |
| 2026-10-05 | `docker run` in Git Bash on Windows fails with `the working directory 'C:/Program Files/Git/work' is invalid`. | Git Bash rewrites `-w /work` into a Windows path. Set `MSYS_NO_PATHCONV=1`, or write `//work`. |
| 2026-10-05 | A container build fails with about 20 × `error CS0579: Duplicate ... attribute`, and the same project builds on the host. | A host build and a container build shared one working tree. Each SDK generated its own `AssemblyInfo.cs`, and the project compiled both. Redirect `BaseIntermediateOutputPath`, `BaseOutputPath` and `NUGET_PACKAGES`, and clean the other toolchain's `obj/` and `bin/` before you build. |

The first three traps come from the workshop preparation, not from a build run.
They are recorded because the cost is known and documented. See
[`workshops/legacy-refactor/TASKS.md`](../../../workshops/legacy-refactor/TASKS.md).
