# Workshop design

The audience, the constraints, the decisions, and the order of the talk.

## Audience

Healthcare software engineers. They write C++ and C#. Their code base is about
5 million lines. It is 15 to 30 years old. Their toolchain has the same age.
IEC 62304 applies to their product.

They expect to learn something new. They do not want a demonstration of tools.

## Goal

Show how to move a large legacy code base safely, with AI assistance, and with
evidence for each step.

The attendees must be able to do two things after the session:

1. Name the reason for a change that they plan, and name the
   [test oracle](../../CONTEXT.md#language-legacy-refactoring) that this reason needs.
2. Read the warnings of their own build, and say for each one whether fixing it
   changes behaviour.

The session does **not** teach the attendees to install and operate the full
method in two hours. That is not possible. The repository remains available
after the session.

## Constraints

| Constraint | Consequence |
| --- | --- |
| The slot is 2 hours. | About 90 minutes of content. The remainder is introductions and questions. Confirm the real length at the preparation meeting on Tuesday 2026-10-06. |
| **Both events are in person.** | No screen share. No remote fallback. Everything runs from the laptop in the bag, and the cables are my problem. See the equipment list in [TASKS.md](TASKS.md). |
| **There is a preparation meeting first**, Tuesday 2026-10-06 at 13:00. | It is a feedback gate, not a rehearsal. Arrive with the executed notebooks and a list of questions. The answers decide Wednesday. |
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

- `-warnaserror:CS0618` promotes the obsolete warning that the library already
  carries. One flag, and no source edit at all. The `[Obsolete(..., error: true)]`
  attribute looks neater but reports fewer places, which `01a_find_obsolete_call_sites`
  measured. Say that on stage: a correction found by running the thing is good
  material, not a weakness.
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

## The two events

| When | What it is for |
| --- | --- |
| Tuesday 2026-10-06, 13:00 | Preparation meeting. Show that the method is real, and ask what the room needs. The question list is in [TASKS.md](TASKS.md). |
| Wednesday 2026-10-07, 14:00 | The workshop itself, in the order below. |

The best outcome of Tuesday is permission to run the warning triage of
`01_build_warnings` against one of their own modules on Wednesday. That turns a
demonstration on a public DICOM library into a reading of their own code base,
which is a different kind of evidence.

## Order of the talk

The notebook numbers follow the software lifecycle. The talk does not. Say this
difference clearly. It shows that you can read the notebooks in any order.

| Time | Block | On the screen |
| --- | --- | --- |
| 0:00–0:15 | Introductions. Their code base. Their regulatory context. | — |
| 0:15–0:25 | **Why you would refactor at all**, with the five reasons. Then the problem and the claims. The example code is a stand-in. Size does not change the method. | The five reasons, then the oracle ladder |
| 0:25–0:40 | `00_setup`. I did not build an environment. I built the skill that builds it. A pinned toolchain is evidence under IEC 62304. | Image digest, toolchain versions, the learned-environments diff |
| 0:40–1:10 | `01_build_warnings`. **The proof.** Eleven warnings are four decisions. Three fix attempts, all judged by the compiler. | The warning count falling 11 → 10 → 3, and the three rejected attempts |
| 1:10–1:40 | `02_test_driven_development`. The three warnings that change behaviour. A failing test first for the defect, and no failing test allowed for the refactor. | The red test, then green. Coverage of the lines before the edit |
| 1:40–1:50 | `01a_find_obsolete_call_sites`. **Spare block.** Remove this block first. The same call sites, counted by a text search and by the compiler. | Text-search count against compiler count. The diff. The miss. |
| 1:50–1:57 | Transfer. The pinned installation. Subversion and ClearCase. The on-premises model. | [ADR 003](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md) |
| 1:57–2:00 | End. One URL. | The repository |

### Spare time

Questions use the end of a session, not the start. Therefore the proof runs
early.

Remove blocks in this order when time is short: `01a`, then the transfer block.
The session is complete if only the first five blocks run, which ends on `02`.
Say early that all material is published. An interrupted demonstration then
costs nothing.

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
