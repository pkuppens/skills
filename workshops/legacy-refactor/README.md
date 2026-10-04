# Workshop — AI-assisted refactoring of large legacy code bases

A 2-hour workshop. It shows a way of working, not a tool tour.

The subject is a code base that is larger than any context window. The example
code is a public healthcare code base. The method does not depend on the size
of the code base.

## The claim

Generation is cheap. A trustworthy verdict is scarce.

Therefore the bottleneck is not the context window. The bottleneck is the
**oracle**: the tool that tells you two things. The change is complete. The
change does not change the behavior.

Build the oracle first. Then let the oracle drive the work.

Full argument: [THESIS.md](THESIS.md).

## How to follow this workshop

You can use three levels of detail. Each level needs more tools than the level
before it.

| Level | What you need | What you get |
| --- | --- | --- |
| 1. Read | A web browser | Every notebook, with the stored output of each cell. |
| 2. Clone and read | Git | The same content on your own disk. |
| 3. Clone and run | Git, Docker, and a model API key | A new run with your own code base. |

Level 1 is enough to follow the session. The notebooks hold the output of each
cell, so the workshop does not need a network connection.

```bash
git clone https://github.com/pkuppens/skills.git
cd skills/workshops/legacy-refactor
```

## The notebooks

The numbers show the order of the software lifecycle. They do not show the order
of the presentation. Read each notebook alone. Each notebook starts with a
header cell that tells you what it proves.

| Notebook | Subject | Skill that it proves |
| --- | --- | --- |
| `00_setup` | The development environment is a versioned artifact. | [`legacy-build-container`](../../skills/legacy-build-container/SKILL.md) |
| `01_precondition_checks` | Which oracles does this code base have? | [`call-site-exhaustiveness`](../../skills/call-site-exhaustiveness/SKILL.md) |
| `02_requirements_engineering` | Reconstruct the intent before you change the code. | `intent-layer-reconstruction` |
| `03_test_driven_development` | Build the output test before you change the code. | `golden-output-regression` |
| `04_bug_investigation` | Find the cause with an oracle, not with a text search. | [`oracle-first-refactor`](../../skills/oracle-first-refactor/SKILL.md) |
| `05_refactoring` | Let the compiler find every call site. | [`call-site-exhaustiveness`](../../skills/call-site-exhaustiveness/SKILL.md) |
| `06_transfer` | How to use this method in your own team. | [`skills-transfer`](../../skills/skills-transfer/SKILL.md) |

See [notebooks/README.md](notebooks/README.md) for the rules that each notebook
must obey.

## The deliverable is a skill, not an environment

Each notebook proves that one **skill** works. A skill is a set of instructions
that an agent reads. The skills are in [`skills/`](../../skills/) in this
repository. You can install them. See [`06_transfer`](notebooks/) or the
[repository README](../../README.md).

This is the important part. A Dockerfile solves one problem one time. A skill
that writes the correct Dockerfile for your toolchain solves the problem again
for each new toolchain. The notebook output is the proof that the skill works.

## The example code

| Code base | Language | Role |
| --- | --- | --- |
| [fo-dicom](https://github.com/fo-dicom/fo-dicom) | C# | The live demonstration. It has a real legacy API, because the project moved its 1.x methods into a separate package. |
| [DCMTK](https://github.com/DCMTK/dcmtk) | C++ | The proof that the container skill works. It has its own string and list types, because it is older than portable STL. |

Both code bases are DICOM toolkits. The domain is the same as the audience's
domain.

## Documents

| File | Contents |
| --- | --- |
| [PLAN.md](PLAN.md) | The design of the workshop and the order of the talk. |
| [THESIS.md](THESIS.md) | The six claims, and the command that proves each claim. |
| [TASKS.md](TASKS.md) | The preparation tasks, with a gate for each task. |
| [VERIFICATION.md](VERIFICATION.md) | How to verify each claim and each task. |
| [ISSUES.md](ISSUES.md) | The work that remains, and the commands that file it. |

Decisions with a long effect are in [`docs/decisions/`](../../docs/decisions/):

- [ADR 002 — Workshop container environment](../../docs/decisions/002-workshop-container-environment.md)
- [ADR 003 — AI assistance, network, and confidentiality](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md)

## Licence

The workshop material uses the licence of this repository. See
[LICENSE](../../LICENSE). The example code bases keep their own licences.
