# Workshop — AI-assisted refactoring of large legacy code bases

A 2-hour workshop. It shows how to work. It is not a demonstration of tools.

The subject is a code base that is too large for an AI agent to read at one
time. The example code is a public healthcare code base. The method works for
any size, because the method does not read the whole code base.

## Why you would do this

Nobody changes old code because the code is old. There must be a reason. A
defect that you must fix. A function that a client needs. A platform that no
longer gets security updates. Code that nobody understands. Code that has no
tests.

In all five cases you need the same two answers first. **Where is this code
used? Did I change the behavior?**

Reasons and examples: [THESIS.md](THESIS.md#why-refactor-legacy-code).

## The claim

An AI agent writes code quickly. It is much more difficult to know whether the
new code is correct.

So the difficult part is proof, not search. You need a tool that proves two
things. The change is complete. The change does not change the behavior. This
workshop calls such a tool an **oracle**.

Make the oracle first. Then let the oracle direct the work.

All six claims: [THESIS.md](THESIS.md).

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

The numbers give the order of the software lifecycle. They do not give the order
of the talk. Read each notebook alone. Each notebook starts with a
header cell that tells you what it proves.

| Notebook | Subject | Skill that it proves |
| --- | --- | --- |
| `00_setup` | The build environment is a file that you can version and share. | [`legacy-build-container`](../../skills/legacy-build-container/SKILL.md) |
| `01_precondition_checks` | Which oracles does this code base already have? | [`call-site-exhaustiveness`](../../skills/call-site-exhaustiveness/SKILL.md) |
| `02_requirements_engineering` | Write down what the code must do, before you change it. | `intent-layer-reconstruction` |
| `03_test_driven_development` | Make the output comparison before you change the code. | `golden-output-regression` |
| `04_bug_investigation` | Find the cause of a defect with an oracle, not with a text search. | [`oracle-first-refactor`](../../skills/oracle-first-refactor/SKILL.md) |
| `05_refactoring` | Let the compiler find every place that calls the old function. | [`call-site-exhaustiveness`](../../skills/call-site-exhaustiveness/SKILL.md) |
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
| [DCMTK](https://github.com/DCMTK/dcmtk) | C++ | The proof that the container skill works. It has its own string and list types, because it is older than the standard C++ library. |

Both code bases are DICOM toolkits. The domain is the same as the audience's
domain.

## Documents

| File | Contents |
| --- | --- |
| [PLAN.md](PLAN.md) | The design of the workshop and the order of the talk. |
| [THESIS.md](THESIS.md) | Why you refactor at all, the six claims, and the command that proves each claim. |
| [TASKS.md](TASKS.md) | The preparation tasks, with a gate for each task. |
| [VERIFICATION.md](VERIFICATION.md) | How to verify each claim and each task. |
| [ISSUES.md](ISSUES.md) | The work that remains, and the commands that file it. |

Decisions with a long effect are in [`docs/decisions/`](../../docs/decisions/):

- [ADR 002 — Workshop container environment](../../docs/decisions/002-workshop-container-environment.md)
- [ADR 003 — AI assistance, network, and confidentiality](../../docs/decisions/003-ai-assistance-network-and-confidentiality.md)
- [ADR 004 — Licensing split](../../docs/decisions/004-licensing-split.md)

## Licence

**This workshop is not MIT licensed. The skills are.**

| What | Licence | What you may do |
| --- | --- | --- |
| This directory and everything in it | [CC BY-NC-ND 4.0](../LICENSE) | Read it, keep it, and share it without change. You may not sell it and you may not publish a changed version. |
| [`skills/`](../../skills/) | [MIT](../../LICENSE) | Use it, change it, and build on it. Commercial use is allowed. |
| The example code bases | Their own licences | See fo-dicom and DCMTK. |

So: **learn from the workshop, build with the skills.** If you want to use this
method on your own code, use the skills. That is what they are for.

Reasons for the split: [ADR 004](../../docs/decisions/004-licensing-split.md).
