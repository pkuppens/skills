# Notebook rules

Each notebook must obey these rules. The rules make the notebooks usable
offline, readable alone, and honest.

## 1. Store the output in Git

Commit each notebook **with** the output of each cell.

The stored output makes the notebook three things at the same time: the
runbook, the recording, and the handout. A reader needs only a browser.

**Do not add a tool that strips output.** `nbstripout` deletes the stored
output. The workshop then has no offline fallback. This repository has no
`pre-commit` configuration at this time. Keep it that way for this directory,
or exclude this directory.

## 2. Never store output that the cell did not produce

This is the most important rule.

A notebook that says "this cell was not run" is acceptable. A notebook with
invented output is a defect. In a regulated context it is worse: the artifact
becomes evidence, and false evidence has no value.

Mark an unfinished notebook in its header cell. Use the word `PLANNED`.

## 3. Use the standard header cell

Each notebook starts with one Markdown cell. The cell has these five lines:

```markdown
# NN — Title

**Proves:** which claim from ../THESIS.md
**Skill:** which skill in ../../../skills/ this notebook exercises
**Needs:** the tools, the images, and the network state
**Run time:** the measured time of a full run
**State:** EXECUTED or PLANNED
```

## 4. Each notebook stands alone

A question can change the order of the session. Therefore a notebook must not
depend on a variable from another notebook.

Each notebook sets up what it needs. Each notebook says what it assumes. If a
notebook needs an image from `00_setup`, then it must check that the image
exists and must say so.

## 5. Keep the cells small

One idea per cell. A reader must be able to find the cell that produces a
number that the talk mentions.

Put the long output in a file and show a summary in the cell, when the raw
output is longer than one screen.

## 6. Mark the decisions

A decision with a long effect belongs in `docs/decisions/` as an ADR. A
notebook cell summarizes the decision and links to the ADR. Do not write a
decision twice.

Current ADRs:

- [ADR 002 — Workshop container environment](../../../docs/decisions/002-workshop-container-environment.md)
- [ADR 003 — AI assistance, network, and confidentiality](../../../docs/decisions/003-ai-assistance-network-and-confidentiality.md)

## 7. Show the oracle, not the tool

A cell must answer a question from [THESIS.md](../THESIS.md). A cell that only
shows a tool version is setup, not content. Keep the setup cells together at
the start.

## Planned notebooks

| Notebook | State |
| --- | --- |
| `00_setup.ipynb` | To do. Tier A. |
| `01_precondition_checks.ipynb` | To do. Tier A. |
| `02_requirements_engineering.ipynb` | To do. Tier C. |
| `03_test_driven_development.ipynb` | To do. Tier B. |
| `04_bug_investigation.ipynb` | To do. Tier C. |
| `05_refactoring.ipynb` | To do. Tier A. The headline. |
| `06_transfer.ipynb` | To do. Tier C. |

The tiers and the gates are in [../TASKS.md](../TASKS.md).
