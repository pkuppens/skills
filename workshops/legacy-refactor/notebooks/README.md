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
is wanted later. The rule is not
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

## 3. Start with the summary, then the details

A reader decides in the first screen whether to read on. So each notebook
starts with plain words, and the bookkeeping comes after.

1. **The first cell: `# NN — Title`, then `## In short`.** The goal, why it
   comes first, how, and the result, in a few sentences each. Then the stations
   and the things to remember.
2. **The second cell: how to run it.** The `uv` commands, and a table of
   pitfalls that a real run hit.
3. **At the end of that cell: `### About this notebook`**, a small table:

| | |
| --- | --- |
| **Skill** | which skill in ../../../skills/ this notebook exercises |
| **Needs** | the tools, the images, and the network state |
| **Run time** | the measured time of a full run |
| **State** | EXECUTED or PLANNED |
| **Supports** | which claim from ../CLAIMS.md, in one line |

`00_setup` follows this layout. `01` and `01a` still use the older five-line
header, and change when they are next rebuilt.

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

A cell must answer a question from [CLAIMS.md](../CLAIMS.md). A cell that only
shows a tool version is setup, not content. Keep the setup cells together at
the start.

## How a notebook is authored

A notebook's cells are written by a small `build_NN.py` script next to it, and
the outputs come from a real kernel run:

```bash
cd workshops/legacy-refactor
uv sync        # once: Python and packages from uv.lock
cd ../..       # build scripts run from the repo root

# 1. write the cells, no outputs
uv run --project workshops/legacy-refactor python workshops/legacy-refactor/notebooks/build_00.py

# 2. run every cell, and store the outputs
uv run --project workshops/legacy-refactor jupyter nbconvert --to notebook --execute --inplace workshops/legacy-refactor/notebooks/00_setup.ipynb
```

`--inplace` replaces the stored results. Use it only to update the committed
notebook. To try a notebook, write to `--output my_NN.ipynb` instead (see
[../SETUP.md](../SETUP.md)).

The script never writes an output value. That is deliberate: it makes rule 2
structural rather than a promise. If a cell did not run, the notebook has no
output for it, and that is visible.

## Planned notebooks

| Notebook | State |
| --- | --- |
| `00_setup.ipynb` | **EXECUTED.** Tier A. The build environment is a skill. |
| `01_build_warnings.ipynb` | **EXECUTED.** Tier A. Eleven warnings, four decisions. |
| `02_test_driven_development.ipynb` | To do. Tier A. The three warnings that change behaviour. |
| `01a_find_obsolete_call_sites.ipynb` | **EXECUTED.** Appendix to `01`. The full text-search against compiler count for one obsolete type. |

The session is three notebooks: `00`, `01`, `02`. `01a` stays because it is
executed and it measures the text-search comparison that `01` cites, but the
talk can drop it when time is short.

**Why `01a` and not `05`.** The first plan (commit `751a960`) had seven
notebooks, numbered by lifecycle: `00_setup`, `01_precondition_checks`,
`02_requirements_engineering`, `03_test_driven_development`,
`04_bug_investigation`, `05_refactoring`, `06_transfer`. Four were dropped for
this session (precondition checks, requirements engineering, bug
investigation, transfer), and test-driven development moved up to `02`. The
call-site notebook was renamed `01a` because it is the deep dive behind
station 5 of `01`. The dropped subjects get a number only when they are
written.

