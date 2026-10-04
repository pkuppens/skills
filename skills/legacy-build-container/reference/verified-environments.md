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

## Verified rows

None yet. This file was created on 2026-10-04 with the skill.

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

The first three traps come from the workshop preparation, not from a build run.
They are recorded because the cost is known and documented. See
[`workshops/legacy-refactor/TASKS.md`](../../../workshops/legacy-refactor/TASKS.md).
