# ADR 002: Container environment for legacy toolchains

**Status:** Accepted
**Date:** 2026-10-04
**Context:** [`workshops/legacy-refactor/`](../../workshops/legacy-refactor/README.md) — the workshop on AI-assisted refactoring of large legacy code bases. The decision also governs the [`legacy-build-container`](../../skills/legacy-build-container/SKILL.md) skill.

## Context

A legacy code base needs a legacy toolchain. A code base that is 15 to 30 years
old can need a compiler of the same age. The current compiler on the developer
machine often cannot build it.

An AI agent cannot help with such a code base if the agent has no build. The
build is the first step of the [test oracle](../../CONTEXT.md#language-legacy-refactoring)
ladder. Without a build, the agent can only guess whether a change is complete.

("Oracle" here is the testing term, not the database vendor. The linked entry
is the single definition for this repository, and it names where the term comes
from.)

There is a second problem. The agent must run where the toolchain runs. If the
source is in one environment and the agent is in another, then the agent cannot
start the compiler.

Three options were considered.

| Option | Setup cost | Reproducible | Can be shared | Risk |
| --- | --- | --- | --- | --- |
| A. Native build in WSL2 or on the host | Low | No | No | Low |
| B. Docker container with a pinned image | Medium | Yes | Yes | Medium |
| C. Kubernetes with a build pod | High | Yes | Yes | High |

## Decision

1. **Use Docker.** The unit is one container with a pinned base image and a
   mounted host workspace.
2. **Run the agent inside the container**, next to the toolchain. State this
   rule in every runbook.
3. **Mount the workspace from the host.** Do not copy the source into the
   image. The source then stays on the host disk, which matters when the source
   is confidential.
4. **Reject Kubernetes.** One container and one workspace do not need an
   orchestrator. Kubernetes adds a cluster, a registry, and a manifest set, and
   it removes nothing. It becomes relevant only when a build matrix must run in
   parallel on shared hardware. That is a separate decision.
5. **Keep WSL2 as the backend only.** On Windows, Docker Desktop uses WSL2.
   WSL2 work is therefore not wasted, but WSL2 is not the artifact that another
   person can reuse.
6. **Pin the base image by digest**, not by tag. A tag moves. A digest does
   not.
7. **Declare the build matrix, even when it holds one entry.** The compiler is
   a sound oracle only for the settings that you build, so the set of settings
   is part of every claim about completeness. Write it as a list with one entry
   and a comment that says why it is one, rather than leaving it out. Adding
   the second entry then costs one line. A parallel matrix across shared
   hardware is a different decision, and it is the trigger to revisit point 4.
   The procedure is step 6 of
   [`legacy-build-container`](../../skills/legacy-build-container/SKILL.md).

## Consequences

**Good.** The image is the artifact. Another engineer can reuse it. Under IEC
62304, a pinned toolchain is evidence of a controlled build environment, not
only a convenience. The image digest, the compiler version, and the build flags
are recordable facts.

**Bad.** Docker must be installed, and that is a new dependency. On a modest
laptop, a large image is slow. Therefore build only the subset of targets that
the work needs.

**Known trap.** Old Linux distributions moved their package servers. An image
such as `ubuntu:14.04` points `apt` at a host that no longer serves packages.
Use `old-releases.ubuntu.com`, or use a Debian image with
`archive.debian.org`. Verify this first, because it is the common cause of a
long failure.

This trap is also in the skill, so that an agent meets it without reading this
ADR: see the trap table in
[`legacy-build-container`](../../skills/legacy-build-container/SKILL.md) and the
recorded traps in
[`reference/verified-environments.md`](../../skills/legacy-build-container/reference/verified-environments.md).
Keep the three lists consistent.

**Reversible?** Partly. The notebooks and the skill assume a container. A change
to a native build needs a rewrite of the setup steps, but not of the method.

## Revisit when

- The build matrix grows past one entry **and** the entries must run in
  parallel on shared hardware. Then evaluate an orchestrator again. A matrix
  that runs one entry after another needs no orchestrator.
- A toolchain exists only as a Windows installer. Then a Windows container or a
  native Windows build is the only option.
- The image exceeds the disk of the target machine. Then split the image per
  language.
