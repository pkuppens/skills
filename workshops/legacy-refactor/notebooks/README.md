# Notebook rules

Each notebook must obey these rules. The rules make the notebooks usable
offline, readable alone, and honest.

## 1. Store the output in Git

Commit each notebook **with** the output of each cell.

The stored output makes the notebook three things at the same time: the
runbook, the recording, and the handout. A reader needs only a browser.

**`nbstripout` must never run on this directory.** It deletes the stored
output, and the workshop then has no offline fallback.

`pre-commit` itself is welcome in this repository, and a minimal configuration
is wanted later — see task C5 in [../TASKS.md](../TASKS.md). The rule is not
"no pre-commit". The rule is that this directory keeps its cell output.

When somebody adds the configuration, `nbstripout` must be absent or excluded:

```yaml
# .pre-commit-config.yaml
# nbstripout is deliberately NOT enabled. It strips notebook cell output, and
# workshops/ depends on that output being committed: it is the offline
# fallback and the handout. If you ever enable it, exclude workshops/ as below.
#
# - repo: https://github.com/kynan/nbstripout
#   rev: 0.7.1
#   hooks:
#     - id: nbstripout
#       exclude: ^workshops/
```

Commented out on purpose, with the reason next to it, so that nobody enables it
by accident while adding an unrelated hook.

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

## 7. Show the [test oracle](../../../CONTEXT.md#language-legacy-refactoring), not the tool

A cell must answer a question from [THESIS.md](../THESIS.md). A cell that only
shows a tool version is setup, not content. Keep the setup cells together at
the start.

## How a notebook is authored

A notebook's cells are written by a small `build_NN.py` script next to it, and
the outputs come from a real kernel run:

```bash
python workshops/legacy-refactor/notebooks/build_05.py      # writes cells, no outputs
cd workshops/legacy-refactor/notebooks
jupyter nbconvert --to notebook --execute --inplace 05_refactoring.ipynb
```

The script never writes an output value. That is deliberate: it makes rule 2
structural rather than a promise. If a cell did not run, the notebook has no
output for it, and that is visible.

## Planned notebooks

| Notebook | State |
| --- | --- |
| `00_setup.ipynb` | **EXECUTED.** Tier A. The build environment is a skill. |
| `01_build_warnings.ipynb` | **EXECUTED.** Tier A. Eleven warnings, four decisions. |
| `02_test_driven_development.ipynb` | To do. Tier A. The three warnings that change behaviour. |
| `05_refactoring.ipynb` | **EXECUTED.** Appendix. The call-site count behind `01`, in full. |
| `02_requirements_engineering.ipynb` | Dropped for this session. |
| `04_bug_investigation.ipynb` | Dropped for this session. |
| `06_transfer.ipynb` | Dropped for this session. One slide instead. |

The session is three notebooks: `00`, `01`, `02`. `05` stays because it is
executed and it measures the text-search comparison that `01` cites, but the
talk can drop it when time is short. `01_precondition_checks` was specified and
dropped: it asked a vaguer question than the warnings do.

The tiers and the gates are in [../TASKS.md](../TASKS.md).
