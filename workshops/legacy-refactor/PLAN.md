# Workshop design

The audience, the constraints, the decisions, and the order of the talk.

## Audience

Healthcare software engineers. They write C++ and C#. Their code base is about
5 million lines. It is 15 to 30 years old. Their toolchain has the same age.
IEC 62304 applies to their product.

They expect a new insight. They do not want a tool tour.

## Goal

Show how to move a large legacy code base safely, with AI assistance, and with
evidence for each step.

The attendees must be able to do two things after the session:

1. Name the oracle ladder, and name the oracle for a change that they plan.
2. Run the precondition check against their own code base.

The session does **not** teach the attendees to install and operate the full
method in two hours. That is not possible. The repository remains available
after the session.

## Constraints

| Constraint | Consequence |
| --- | --- |
| The slot is 2 hours. | About 90 minutes of content. The remainder is introductions and questions. |
| A modest laptop runs the demonstration. | Small images. Short builds. No warm cache. |
| Assume no network and no model API. | Every claim must be provable from committed files. |
| The attendees follow the session on their own equipment. | The artifact is a public repository with stored notebook output. |
| Do not fight a build on stage. | The example code is vendored, restored, and built before the session. |
| Questions can interrupt the order. | Each notebook must stand alone. |

## Decisions

| Subject | Decision | Reason |
| --- | --- | --- |
| Environment | Docker. | It is the artifact that the attendees can reuse. See [ADR 002](../../docs/decisions/002-workshop-container-environment.md). |
| Orchestration | No Kubernetes. | One container and one workspace do not need it. See ADR 002. |
| Format | Jupyter notebooks. Store the output of each cell in Git. | The notebook is then the runbook, the recording, and the handout. It needs no network. |
| Live language | C#. | `dotnet build` replaces CMake. C# is easier to read under the stress of a presentation. |
| C++ | Stored output only. Never built on stage. | It proves that the container skill works. It is the largest build risk. |
| Live installation from a third-party repository | Do not do it. | Show the pinned command and the verify output instead. |
| Upstream pull request | Prepare it. Open it after the interview. | An upstream review cycle is outside my control. |

### Why C# for the live demonstration

C# is the better choice for the live part, and it makes a stronger argument
than C++.

- `[Obsolete("message", error: true)]` is one attribute. It needs no build
  flags. Every call site becomes a compile error.
- Roslyn is a semantic index. It needs no compilation database. Step 2 of the
  ladder is therefore free.
- `dotnet build` is one command. CMake leaves the live path.
- In C++, the compiler finds almost every call site. The ladder then looks like
  one step. In legacy C#, reflection, string keys, and generated designer files
  produce call sites that **neither the text search nor the compiler** can see.

The last point is the important one. The demonstration shows the oracle fail.
Then it shows what to do next. A visible limit is more credible than a clean
result, and it gives a reason for steps 3 and 4 of the ladder.

## Example code

| Code base | Language | Role | Why |
| --- | --- | --- | --- |
| fo-dicom | C# | Live demonstration | The project moved its 1.x methods into a separate `fo-dicom.Legacy` package. The migration is therefore real and documented upstream. Older releases target .NET Framework 4.5.2, so a pinned old tag gives period code. |
| DCMTK | C++ | Stored output only | It has `OFString`, `OFList`, and `OFCondition`, because it is older than portable STL. Build `ofstd` and `dcmdata` only. |
| ClearCanvas | C# | One read-only slide | It is the truest legacy: an unmaintained DICOM and PACS platform on .NET Framework. It does not build in a Linux container, so it is not used live. |

## Order of the talk

The notebook numbers follow the software lifecycle. The talk does not. Say this
difference out loud. It shows that the notebooks have random access.

| Time | Block | On the screen |
| --- | --- | --- |
| 0:00–0:15 | Introductions. Their code base. Their regulatory context. | — |
| 0:15–0:25 | The problem and the thesis. The example code is a proxy. Size does not change the method. | The oracle ladder |
| 0:25–0:40 | `00_setup`. I did not build an environment. I built the skill that builds it. A pinned toolchain is evidence under IEC 62304. | Image digest, toolchain versions, the learned-environments diff |
| 0:40–0:55 | `01_precondition_checks`. The most reusable artifact of the session. | The readiness table, both languages |
| 0:55–1:20 | `05_refactoring`. **The proof.** It ends on the call site that neither method found. | Text-search count against compiler count. The diff. The miss. |
| 1:20–1:30 | `03_test_driven_development`. It compiles, the tests pass, and it is still not proof. | The deliberate failure |
| 1:30–1:40 | `02_requirements_engineering`. The first AI deliverable is intent. | The glossary and the invariants |
| 1:40–1:48 | `04_bug_investigation`. **Spare block.** Remove this block first. | The ladder on a real issue |
| 1:48–1:57 | Transfer. The pinned installation. Subversion and ClearCase. The on-premises model. | [ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md) |
| 1:57–2:00 | End. One URL. | The repository |

### Spare time

Questions use the end of a session, not the start. Therefore the proof runs
early.

Remove blocks in this order when time is short: `04`, then `02`, then `03`. The
session is complete if only the first five blocks run. Say early that all
material is published. An interrupted demonstration then costs nothing.

## Version control

This method needs cheap branches, a cheap revert, and bisect. The deliberate
breakage in claim 2 is a branch technique.

Subversion and ClearCase make these operations expensive. The method still
works, but the loop becomes slower, and the team must agree on a different
branch discipline. Name this limit in the transfer block. Do not hide it.

## Confidentiality

The attendees will ask whether their source code must go to a cloud model. The
answer is no, and the answer is part of the method. See
[ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md)
and the [`ai-factory`](../../skills/ai-factory/SKILL.md) skill: confidential
work stays on-premises, and public work goes to the cloud.

Raise this subject before the audience raises it.
